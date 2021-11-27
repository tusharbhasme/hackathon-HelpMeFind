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
    ChoicePrompt,
    ConfirmPrompt,
    PromptOptions,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models.enums import Department, Location
from data_models.help_data import HelpData


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
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

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
        step_context.values["dept"] = dept.value
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
                choices=[Choice(e.name) for e in Location],
            ),
        )

    async def details_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        location = Location(step_context.result.value)
        step_context.values["location"] = location.value
        if step_context.values["action"] == 'Save':
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(prompt=MessageFactory.text("Please enter the details.")),
            )
        else:
            #TODO get data
            await step_context.context.send_activity(
                MessageFactory.text("Here is the data")
            )
        return await step_context.end_dialog()

    async def confirm_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        details = step_context.result
        step_context.values["details"] = details
        values = step_context.values
        await step_context.context.send_activity(
            MessageFactory.text(
                f"You have entered below info for {values['section']} of {values['dept']} department at {values['location']}")
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
            help_data.section = values['section']
            help_data.location = Location(values['location'])
            help_data.details = values['details']
            #TODO save data
            await step_context.context.send_activity(
                MessageFactory.text("Thanks, data has been added successfully!")
            )
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Discarded the data, please try again")
            )
        return await step_context.end_dialog()
