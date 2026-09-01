from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Conversation
from app.schemas import MessageCreate
from app.agent import analyze_multiple_operations
from app.actions import execute_action


def create_message(
    message: MessageCreate,
    db: Session,
):
    conversation = db.query(Conversation).filter(
        Conversation.customer_id == message.customer_id,
        Conversation.status == "active",
    ).first()

    if not conversation:
        conversation = Conversation(
            customer_id=message.customer_id,
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

    if conversation.pending_field == "new_address":
        try:
            analysis = analyze_multiple_operations(message.message)
        except RuntimeError as e:
            raise HTTPException(
                status_code=503,
                detail=str(e),
            )

        new_address = None

        for operation in analysis.operations:
            if operation.new_address:
                new_address = operation.new_address
                break

        if new_address:
            action_result = execute_action(
                "address_change",
                conversation.pending_account_id,
                message.customer_id,
                new_address,
                None,
                db,
            )

            if action_result["success"]:
                conversation.pending_intent = None
                conversation.pending_account_id = None
                conversation.pending_field = None

                db.commit()

                return {
                    "conversation_id": conversation.id,
                    "analysis": analysis,
                    "action": action_result,
                    "customer_message": (
                        "Your address has been updated successfully."
                    ),
                }

            return {
                "conversation_id": conversation.id,
                "analysis": analysis,
                "action": action_result,
            }

    try:
        analysis = analyze_multiple_operations(message.message)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    results = []
    pending_operation = None

    for operation in analysis.operations:

        if (
            operation.intent == "address_change"
            and operation.account_id
            and not operation.new_address
        ):
            pending_operation = operation
            continue

        result = execute_action(
            operation.intent,
            operation.account_id,
            message.customer_id,
            operation.new_address,
            operation.refund_reason,
            db,
        )

        results.append({
            "intent": operation.intent,
            "result": result,
        })

    if pending_operation:
        conversation.pending_intent = pending_operation.intent
        conversation.pending_account_id = pending_operation.account_id
        conversation.pending_field = "new_address"

        db.commit()

    if pending_operation:

        if results:
            successful_actions = [
                item
                for item in results
                if item["result"]["success"]
            ]

            if successful_actions:
                message_text = (
                    "I've completed the available request. "
                    "What would you like your new address to be?"
                )
            else:
                message_text = (
                    "I need your new address to complete "
                    "the address change."
                )
        else:
            message_text = (
                "I'd be happy to help change your address. "
                "What would you like your new address to be?"
            )

        return {
            "conversation_id": conversation.id,
            "analysis": analysis,
            "results": results,
            "pending_operation": {
                "intent": pending_operation.intent,
                "account_id": pending_operation.account_id,
            },
            "customer_message": message_text,
        }

    return {
        "conversation_id": conversation.id,
        "analysis": analysis,
        "results": results,
    }