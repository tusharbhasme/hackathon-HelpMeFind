# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import UserProfile
from data_models.enums import Department, HealthcareSection, Location
from data_models.help_data import HelpData
from dialogs.user_dialog_helper import db_insert_data


class InformationDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(InformationDialog, self).__init__(InformationDialog.__name__)

        self.help_data_accessor = user_state.create_property("HelpData")
        self.add_dialog(WaterfallDialog("help_flow", [
            self.action_step,
            self.department_step,
            self.help_type_step,
            self.location_step,
            self.details_step,
            self.confirm_step,
            self.save_step,
        ]))

        # self.user_profile_accessor = user_state.create_property("UserProfile")
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.transport_step,
                    self.name_step,
                    self.name_confirm_step,
                    self.age_step,
                    self.picture_step,
                    self.confirm_step,
                    self.summary_step,
                ],
            )
        )
        self.add_dialog(
            NumberPrompt(NumberPrompt.__name__, InformationDialog.age_prompt_validator)
        )
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            AttachmentPrompt(
                AttachmentPrompt.__name__, InformationDialog.picture_prompt_validator
            )
        )

        self.initial_dialog_id = "help_flow"

    async def action_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Are you looking to save info or find?"),
                choices=[Choice("Save"), Choice("Find")],
            ),
        )

    async def department_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        action = step_context.result.value
        step_context.values["action"] = action
        if action == "Find":
            await step_context.context.send_activity(
                "My database is currently empty. Please feed some data first"
            )
            return await step_context.end_dialog()
        elif action == "Save":
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Select a department for the data"),
                    choices=[Choice("Healthcare"), Choice("HR"), Choice("Finance")],
                ),
            )

    async def help_type_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        dept = Department(step_context.result.value)
        step_context.values["dept"] = dept
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Select a section of the department"),
                choices=[Choice(e) for e in dept.get_sections()],
            ),
        )

    async def location_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        section = step_context.result.value
        step_context.values["section"] = section
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Select a location"),
                choices=[Choice(e) for e in Location],
            ),
        )

    async def details_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        location = Location(step_context.result.value)
        step_context.values["section"] = location
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter the details.")),
        )

    async def confirm_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        details = step_context.result.value
        step_context.values["details"] = details
        values = step_context.values
        await step_context.context.send_activity(
            MessageFactory.text(f"You have entered below info for {values['section']} of {values['dept']} department")
        )
        await step_context.context.send_activity(details)
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Does it look ok?")
            ),
        )

    async def save_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            help_data: HelpData = await self.help_data_accessor.get(
                step_context.context, HelpData
            )
            values = step_context.values
            help_data.department = Department(values['dept'])
            db_insert_data(help_data)
            #TODO save data

    async def transport_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter your mode of transport."),
                choices=[Choice("Car"), Choice("Bus"), Choice("Bicycle")],
            ),
        )

    async def name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["transport"] = step_context.result.value

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Please enter your name.")),
        )

    async def name_confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["name"] = step_context.result

        # We can send messages to the user at any point in the WaterfallStep.
        await step_context.context.send_activity(
            MessageFactory.text(f"Thanks {step_context.result}")
        )

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Would you like to give your age?")
            ),
        )

    async def age_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            # User said "yes" so we will be prompting for the age.
            # WaterfallStep always finishes with the end of the Waterfall or with another dialog,
            # here it is a Prompt Dialog.
            return await step_context.prompt(
                NumberPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please enter your age."),
                    retry_prompt=MessageFactory.text(
                        "The value entered must be greater than 0 and less than 150."
                    ),
                ),
            )

        # User said "no" so we will skip the next step. Give -1 as the age.
        return await step_context.next(-1)

    async def picture_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        age = step_context.result
        step_context.values["age"] = age

        msg = (
            "No age given."
            if step_context.result == -1
            else f"I have your age as {age}."
        )

        # We can send messages to the user at any point in the WaterfallStep.
        await step_context.context.send_activity(MessageFactory.text(msg))

        if step_context.context.activity.channel_id == "msteams":
            # This attachment prompt example is not designed to work for Teams attachments, so skip it in this case
            await step_context.context.send_activity(
                "Skipping attachment prompt in Teams channel..."
            )
            return await step_context.next(None)

        # WaterfallStep always finishes with the end of the Waterfall or with another dialog; here it is a Prompt
        # Dialog.
        prompt_options = PromptOptions(
            prompt=MessageFactory.text(
                "Please attach a profile picture (or type any message to skip)."
            ),
            retry_prompt=MessageFactory.text(
                "The attachment must be a jpeg/png image file."
            ),
        )
        return await step_context.prompt(AttachmentPrompt.__name__, prompt_options)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["picture"] = (
            None if not step_context.result else step_context.result[0]
        )

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.
        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Is this ok?")),
        )

    async def summary_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            # Get the current profile object from user state.  Changes to it
            # will saved during Bot.on_turn.
            user_profile = await self.user_profile_accessor.get(
                step_context.context, UserProfile
            )

            user_profile.transport = step_context.values["transport"]
            user_profile.name = step_context.values["name"]
            user_profile.age = step_context.values["age"]
            user_profile.picture = step_context.values["picture"]

            msg = f"I have your mode of transport as {user_profile.transport} and your name as {user_profile.name}."
            if user_profile.age != -1:
                msg += f" And age as {user_profile.age}."

            await step_context.context.send_activity(MessageFactory.text(msg))

            if user_profile.picture:
                await step_context.context.send_activity(
                    MessageFactory.attachment(
                        user_profile.picture, "This is your profile picture."
                    )
                )
            else:
                await step_context.context.send_activity(
                    "A profile picture was saved but could not be displayed here."
                )
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Thanks. Your profile will not be kept.")
            )

        # WaterfallStep always finishes with the end of the Waterfall or with another
        # dialog, here it is the end.
        return await step_context.end_dialog()

    @staticmethod
    async def age_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        # This condition is our validation rule. You can also change the value at this point.
        return (
            prompt_context.recognized.succeeded
            and 0 < prompt_context.recognized.value < 150
        )

    @staticmethod
    async def picture_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if not prompt_context.recognized.succeeded:
            await prompt_context.context.send_activity(
                "No attachments received. Proceeding without a profile picture..."
            )

            # We can return true from a validator function even if recognized.succeeded is false.
            return True

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        # If none of the attachments are valid images, the retry prompt should be sent.
        return len(valid_images) > 0
