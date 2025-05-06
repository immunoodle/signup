from nicegui import ui
from email.utils import parseaddr
import grpc
import dex_pb2
import dex_pb2_grpc
import uuid
import bcrypt
import random, os
from dotenv import load_dotenv

load_dotenv()
REDIRECT_URL_AFTER_SIGNUP = os.environ["REDIRECT_URL_AFTER_SIGNUP"]
GRPC_ADDRESS = os.environ["GRPC_ADDRESS"]


############################################################################
# UTILITY FUNCTIONS
############################################################################


def dex_create_user(username, email, password):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = dex_pb2_grpc.DexStub(channel)
        bcrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        create_password_req = dex_pb2.CreatePasswordReq(
            password=dex_pb2.Password(
                user_id=str(uuid.uuid4()),
                email=email,
                username=username,
                hash=bcrypted,
            )
        )
        resp = stub.CreatePassword(create_password_req)
        print(f"Resp: Already Exists? {resp.already_exists}")
        return resp.already_exists


def dex_update_password(email, password):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = dex_pb2_grpc.DexStub(channel)
        bcrypted = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        update_password_req = dex_pb2.UpdatePasswordReq(
            email=email,
            new_hash=bcrypted,
        )
        resp = stub.UpdatePassword(update_password_req)
        print(f"Resp: Not Found? {resp.not_found}")
        return resp.not_found


def dex_delete_user(email):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = dex_pb2_grpc.DexStub(channel)
        delete_password_req = dex_pb2.DeletePasswordReq(email=email)
        resp = stub.DeletePassword(delete_password_req)
        print(f"Resp: Not Found? {resp.not_found}")
        return resp.not_found


############################################################################
# Layout Components
############################################################################


def page_header():
    # with ui.row():
    ui.add_head_html("<style>body {background-color: #efefef; }</style>")

    with ui.header(elevated=True).style(
        "background-color: #ffffff; margin: 0px; padding: 10px 0 10px 25px;"
    ).classes("items-left justify-between"):
        ui.image("https://madi-sandbox.dartmouth.edu/dex/theme/logo.png").style(
            "height: 25px; width: 25px;"
        )


############################################################################
# ROUTES
############################################################################


@ui.page("/forgot_password")
def signup():
    def generate_code() -> None:
        error_count = 0
        if not "@" in parseaddr(email.value)[1]:
            email.error = "Invalid Email Address"
            error_count += 1

        if error_count == 0:
            verification_code = "".join([str(random.randint(1, 9)) for _ in range(6)])
            print(
                f"Password Reset Code '{verification_code}' generated for '{parseaddr(email.value)[1]}'"
            )
            ui.notify(f"Code Generated")
            generate_code_code.set_visibility(False)
            verify_code_card.set_visibility(True)
            reset_password_card.set_visibility(False)

    def verify_code() -> None:
        ui.notify(f"Code Verified")
        # generate_code_code.set_visibility(False)
        # verify_code_card.set_visibility(False)
        # reset_password_card.set_visibility(True)

    def reset_password() -> None:
        ui.notify("Password Reset")
        ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP)

    page_header()

    with ui.column().classes("w-full items-center").style("margin-top: 40px;"):
        with ui.card(align_items="center").tight().style(
            "padding: 30px 0 30px 0; max-width: 500px; min-width: 520px;"
        ) as generate_code_code:
            ui.label("Forgot password").style(
                "margin-bottom: 30px; font-size: 200%; font-weight: 300"
            )
            email = (
                ui.input(
                    placeholder="Email Address",
                    validation={},
                )
                .props("outlined dense")
                .style("width: 250px;")
            )

            with ui.row():
                ui.button("Generate Reset Code", on_click=generate_code)
                ui.button(
                    "Cancel",
                    on_click=lambda: ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP),
                    color="secondary",
                )

        with ui.card(align_items="center").tight().style(
            "padding: 30px 0 30px 0; max-width: 500px; min-width: 520px;"
        ) as verify_code_card:
            ui.label("Veirfy Reset Code").style(
                "margin-bottom: 30px; font-size: 200%; font-weight: 300"
            )
            ui.input(
                placeholder="Code",
                validation={},
            ).props(
                "outlined dense"
            ).style("width: 250px;")

            with ui.row():
                ui.button("Verify", on_click=verify_code)
                ui.button(
                    "Cancel",
                    on_click=lambda: ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP),
                    color="secondary",
                )

        with ui.card(align_items="center").tight().style(
            "padding: 30px 0 30px 0; max-width: 500px; min-width: 520px;"
        ) as reset_password_card:
            ui.label("Reset Password").style(
                "margin-bottom: 30px; font-size: 200%; font-weight: 300"
            )
            password = (
                ui.input(
                    placeholder="New Password",
                    validation={},
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .style("width: 250px;")
            )
            password_confirm = (
                ui.input(
                    # label="Text",
                    placeholder="Confirm Password",
                    # on_change=lambda e: result.set_text("you typed: " + e.value),
                    validation={},
                    # validation={"Input too long": lambda value: len(value) < 20},
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .style("width: 250px; padding-bottom: 30px;")
            )

            with ui.row():
                ui.button("Reset Password", on_click=reset_password)
                ui.button(
                    "Cancel",
                    on_click=lambda: ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP),
                    color="secondary",
                )

        generate_code_code.set_visibility(True)
        verify_code_card.set_visibility(False)
        reset_password_card.set_visibility(False)


@ui.page("/signup")
def signup():
    def try_signup() -> (
        None
    ):  # local function to avoid passing username and password as arguments
        error_count = 0
        if not full_name.value:
            full_name.error = "Missing Full Name"
            error_count += 1
        if not "@" in parseaddr(email.value)[1]:
            email.error = "Invalid Email Address"
            error_count += 1
        if not password.value:
            password.error = "Missing password"
            error_count += 1
        if password.value != password_confirm.value:
            password_confirm.error = "Password doesn't match"
            error_count += 1

        if error_count == 0:
            already_exists = dex_create_user(
                full_name.value, parseaddr(email.value)[1], password.value
            )
            if already_exists:
                ui.notify(
                    f"An account with that email address already exists",
                    color="negative",
                )
            else:
                print(
                    f"Account Created -- Name: {full_name.value}, Email: {parseaddr(email.value)[1]}"
                )
                ui.notify(
                    f"Account Created",
                    color="positive",
                )
                ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP)

    page_header()

    with ui.column().classes("w-full items-center").style("margin-top: 40px;"):
        with ui.card(align_items="center").tight().style(
            "padding: 30px 0 30px 0; max-width: 500px; min-width: 520px;"
        ):
            ui.label("Signup for an account").style(
                "margin-bottom: 30px; font-size: 200%; font-weight: 300"
            )
            full_name = (
                ui.input(
                    placeholder="Full Name",
                    validation={},
                )
                .props("outlined dense")
                .style("width: 250px;")
            )
            email = (
                ui.input(
                    placeholder="Email Address",
                    validation={},
                )
                .props("outlined dense")
                .style("width: 250px;")
            )
            password = (
                ui.input(
                    placeholder="Password",
                    validation={},
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .style("width: 250px;")
            )
            password_confirm = (
                ui.input(
                    # label="Text",
                    placeholder="Confirm Password",
                    # on_change=lambda e: result.set_text("you typed: " + e.value),
                    validation={},
                    # validation={"Input too long": lambda value: len(value) < 20},
                    password=True,
                    password_toggle_button=True,
                )
                .props("outlined dense")
                .style("width: 250px; padding-bottom: 30px;")
            )

            with ui.row():
                ui.button("Signup", on_click=try_signup, color="positive")
                ui.button(
                    "Cancel",
                    on_click=lambda: ui.navigate.to(REDIRECT_URL_AFTER_SIGNUP),
                    color="secondary",
                )
            # result = ui.label()


ui.run(uvicorn_logging_level="info")
