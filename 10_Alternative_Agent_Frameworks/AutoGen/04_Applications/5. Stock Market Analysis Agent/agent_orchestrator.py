import autogen
from tools import FinanceTools
from autogen.agentchat import register_function
from agent_config import AgentConfig

def orchestrate_agents(user_request, finance_reporting_analyst, technical_analyst, strategy_agent, user):
        tools_list = AgentConfig.get_tools_list()
        try:
            # Register tools
            for tool_name, tool_func in [
                ("technical_analysis_tool", FinanceTools.technical_analysis_tool),
                ("risk_assessment_tool", FinanceTools.risk_assessment_tool),
                ("strategy_signal_tool", FinanceTools.strategy_signal_tool)
            ]:
                callers = {
                    "finance_data_fetch": [finance_reporting_analyst],
                    "technical_analysis_tool": [technical_analyst],
                    "risk_assessment_tool": [strategy_agent],
                    "strategy_signal_tool": [strategy_agent]
                }
                for caller in callers[tool_name]:
                    register_function(
                        tool_func,
                        caller=caller,
                        executor=user,
                        name=tool_name,
                        description= tools_list[tool_name]["function"]["description"]
                    )

            groupchat = autogen.GroupChat(
                agents=[user, finance_reporting_analyst, technical_analyst, strategy_agent],
                messages=[],
                max_round=9,
                speaker_selection_method="round_robin"
            )

            manager = autogen.GroupChatManager(
                groupchat=groupchat,
                llm_config={"config_list": AgentConfig.get_llm_config(), "timeout": 280, "temperature": 0.5},
            )

            result = user.initiate_chat(manager, message=user_request)

            if hasattr(result, "chat_history") and result.chat_history:
                for msg in reversed(result.chat_history):
                    if msg.get("name") in ["user", "manager"]:
                        return msg.get("content", "No final output found.")
            if hasattr(result, 'summary'):
                return result.summary
            return "Analysis completed successfully. No detailed result was returned."
        except Exception as e:
            return f"Error during analysis: {str(e)}"