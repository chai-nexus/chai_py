from pathlib import Path
from typing import AnyStr, Optional
import time

from halo import Halo
from requests import HTTPError
from typing_extensions import TypedDict
import requests
import segno

from chai_py.auth import get_auth
from chai_py.cloud_logs import display_logs, get_logs
from chai_py.defaults import ENDPOINT
from chai_py.notebook_utils import IS_NOTEBOOK, show_qr


def upload_and_deploy(package: AnyStr, bot_uid: str = None, useDeployment = True) -> str:
    """Uploads the given archive, triggering deployment of the chatbot.

    :param package: Path to the packaged chatbot zip.
    :param bot_uid: Used to modify an existing bot: the UID of the previously-deployed bot.
    :return bot_uid: The UID of the deployed bot.
    """
    package = Path(package)

    deployment_file = package.parent / "_deployment"

    if deployment_file.exists() and bot_uid is None and useDeployment:
        with deployment_file.open("r") as f:
            previous_bot_uid = f.read().strip()
        print("Detected previous deployment from this location. Use the same bot UID as before?")
        print(f" [y] (default) Yes. Update the bot ({previous_bot_uid}).")
        print(f" [n] No. Deploy as a new bot.")
        input_key = input().lower()
        if input_key == "y" or input_key == "":
            bot_uid = previous_bot_uid
            print(f"Using previous bot UID: {bot_uid}")
        elif input_key == "n":
            pass
        else:
            raise RuntimeError("Unknown input.")

    auth = get_auth()
    try:
        r = requests.post(
            ENDPOINT,
            params={'uid': auth.uid, 'key': auth.key, 'bot_uid': bot_uid}
        )
        try:
            r.raise_for_status()
        except Exception:
            raise RuntimeError(r.json())
    except Exception:
        print(r.content, r.reason)
        raise RuntimeError("Failed to retrieve signed URL.")

    url = r.text
    if bot_uid is None:
        print("Creating new bot.")
        bot_uid = parse_signed_url_for_bot_uid(url)
        print(f"Received bot UID: {bot_uid}")
    with deployment_file.open("w") as f:
        f.write(bot_uid)

    with package.open("rb") as f:
        r = requests.put(url, data=f, headers={'content-type': 'application/zip'})
        r.raise_for_status()
    print(f"Successfully uploaded {package}.")
    return bot_uid


def parse_signed_url_for_bot_uid(url: str):
    """Parses a bot UID from a signed URL.

    Assumes the signed URL follows the following scheme:
        [...]/{bot_uid}.zip?[...]

    :param url:
    :return:
    """
    endpoint = url.split("?", maxsplit=1)[0]
    file_name = endpoint.split("/")[-1]
    bot_uid = file_name.split(".")[0]
    return bot_uid


def wait_for_deployment(bot_uid: str, sleep: float = 3):
    """Waits for deployment of the bot to complete.

    :param bot_uid:
    :param sleep: Polling interval in seconds.
    :return:
    """
    MIN_SLEEP = 1
    sleep = max(MIN_SLEEP, sleep)

    BOT_DEPLOYMENT_PROCESS = [
        "signed_url_created",
        "processing_upload",
        "deploying",
        "initialized",
    ]
    current_deployment_process = -1  # Index for BOT_DEPLOYMENT_PROCESS
    completed_processes = []
    existing_status = None
    try:
        _existing_status = get_bot_status(bot_uid)
        if "activeDeployment" in _existing_status:
            existing_status = _existing_status
            print(f"Found previous deployment: Version {existing_status['activeDeployment']['version']}")
        elif "failedDeployment" in _existing_status:
            existing_status = _existing_status
            print(f"Found previous failed deployment: Version {existing_status['failedDeployment']['version']}")

    except HTTPError as e:
        if e.response.status_code != 404:
            raise e
        else:
            print("Did not find previous deployment.")

    MAXIMUM_ERROR_RETRIES = 10
    error_retries = 0

    start_time = time.time()
    with Halo(text="Polling for progress...") as spinner:
        spinner.start()
        time.sleep(5)  # Initial wait to avoid bot status error.
        while True:
            try:
                status = get_bot_status(bot_uid)
            except Exception as e:
                spinner.warn(f"Error getting bot status (UID: {bot_uid}): {e}")
                error_retries += 1
                if error_retries > MAXIMUM_ERROR_RETRIES:
                    spinner.fail()
                    print(f"Hit retry-on-error limit ({MAXIMUM_ERROR_RETRIES}).")
                    break
                continue
            if existing_status is not None:
                # Check if new timestamp is later than existing timestamp
                existing_deployment = existing_status['activeDeployment'] if 'activeDeployment' in existing_status else existing_status['failedDeployment']
                if status['timestamp'] <= existing_deployment['timestamp']:
                    # Do not parse old version
                    continue
            status_str = status['status']
            if status_str not in BOT_DEPLOYMENT_PROCESS:
                raise ValueError(f"Unknown status: {status_str}.")
            new_current_deployment_process = BOT_DEPLOYMENT_PROCESS.index(status_str)
            if new_current_deployment_process != current_deployment_process:
                # Completed new step(s)
                for step in BOT_DEPLOYMENT_PROCESS[:new_current_deployment_process + 1]:
                    if step in completed_processes:
                        continue
                    spinner.succeed(step)
                    completed_processes.append(step)
                current_deployment_process = new_current_deployment_process
                if current_deployment_process + 1 < len(BOT_DEPLOYMENT_PROCESS):
                    # If next step exists, set spinner to next step
                    spinner.start(
                        f"Waiting for next step: {BOT_DEPLOYMENT_PROCESS[current_deployment_process + 1]}"
                    )
                else:
                    # Next step does not exist; wait for final deployment confirmation
                    spinner.start("Waiting for active_deployment confirmation...")
            if 'activeDeployment' in status:
                new_active_deployment = status['activeDeployment']
                if existing_status is None \
                        or ('activeDeployment' in existing_status
                            and new_active_deployment['version'] > existing_status['activeDeployment']['version']):
                    spinner.succeed("active_deployment")
                    print(f"New active deployment: {new_active_deployment}")
                    break
            if 'failedDeployment' in status:
                new_failed_deployment = status['failedDeployment']
                if existing_status is None \
                        or ('failedDeployment' in existing_status
                            and new_failed_deployment['version'] > existing_status['failedDeployment']['version']):
                    spinner.fail("failed_deployment")
                    display_logs(
                        get_logs(
                            bot_uid=bot_uid,
                            errors=True
                        )
                    )
                    print("Full logs can be checked with the display_logs and get_logs functions.")

                    break
            elapsed_time = time.time() - start_time
            if elapsed_time > 2 * 60:
                print("This deployment is taking an unexpectedly long time.")
            time.sleep(sleep)


class Deployment(TypedDict):
    timestamp: int
    version: int


class BotStatus(TypedDict):
    status: str
    timestamp: int
    activeDeployment: Optional[Deployment]
    failedDeployment: Optional[Deployment]


def get_bot_status(bot_uid: str) -> BotStatus:
    """Gets the status of the bot.

    :param bot_uid:
    :return:
    """
    auth = get_auth()
    try:
        req = requests.get(
            url=ENDPOINT,
            params={
                'uid': auth.uid,
                'key': auth.key,
                'bot_uid': bot_uid,
                'item': 'status'
                }
        )
        try:
            req.raise_for_status()
        except Exception:
            raise RuntimeError(req.json())
    except Exception:
        raise RuntimeError(f"Failed to retrieve status for bot {bot_uid}.")
    return req.json()


def share_bot(bot_uid: str) -> str:
    """Displays the url, a QR code, along with additional guidance.

    :param bot_uid:
    :return: The url for the bot.
    """
    url = f"chai://chai.ml/{bot_uid}"

    qr_code = segno.make_qr(url)
    print("Scan the QR code with your phone to start a chat in the app!")
    print(f"Or check it out at {url}")

    if IS_NOTEBOOK:
        show_qr(qr_code)
    else:
        qr_code.terminal()

    def save():
        path = input("Save QR code to: (Press [Enter] for default: 'qr.png') ")
        if len(path) == 0:
            path = "qr.png"
        qr_code.save(path, scale=10)
        print(f"Saved QR code to {path}.")

    def open_():
        qr_code.show(scale=10)

    actions = {
        "s": (save, "Save this QR code to an image file.")
    }
    if not IS_NOTEBOOK:
        actions["o"] = (open_, "Open QR code in external viewer.")

    while True:
        print("\nEnter one of the following keys to perform additional actions (or [Enter] to exit):")
        for key, action in actions.items():
            print(f" [{key}] {action[1]}")

        input_key = input().lower()
        if input_key in actions:
            actions[input_key][0]()
        else:
            print("Exiting.")
            break

    return url


def delete_bot(bot_uid: str) -> str:
    """
    Uses an HTTPS request to trigger deletion of bot with specified UID.

    :param bot_uid:
    :return: The url for the bot.
    """
    auth = get_auth()
    try:
        req = requests.delete(
            url=ENDPOINT,
            params={'uid': auth.uid, 'key': auth.key, 'bot_uid': bot_uid}
        )
        try:
            req.raise_for_status()
        except Exception:
            raise RuntimeError(req.json())
    except Exception as exc:
        raise RuntimeError(f"Failed to delete bot {bot_uid}.")

    print(f"Successfully deleted {bot_uid}.")
    return bot_uid

advertise_deployed_bot = share_bot
