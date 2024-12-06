from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from .models import PlatformConfig

class ContentGenerationChain:
    def __init__(self, config: PlatformConfig):
        self.config = config
        max_tokens = min(config.max_length, 1000)  # Limite à 8000 tokens pour GPT-4
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=max_tokens
        )
        self.prompt = PromptTemplate(
            template=config.prompt_template,
            input_variables=["tone", "style", "keywords", "task", "target_audience"]
        )
        self.chain = self.prompt | self.llm

    async def generate(self, variables: dict) -> str:
        # Ajout des paramètres spécifiques à la plateforme
        if "platform_params" in variables:
            variables.update(variables["platform_params"])
        result = await self.chain.ainvoke(variables)
        return result.content