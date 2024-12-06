from .chains import ContentGenerationChain
from .models import PlatformConfig, UserInputs, ContentOutput
from .validators import ContentValidator
from .analyzers import ContentAnalyzer

class SocialMediaWriter:
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.generator = ContentGenerationChain(config)
        self.validator = ContentValidator(config)
        self.analyzer = ContentAnalyzer(config)

    async def generate_content(self, task: str, user_inputs: UserInputs) -> ContentOutput:
        content = await self.generator.generate({
            "task": task,
            "tone": user_inputs.tone,
            "style": user_inputs.style,
            "target_audience": user_inputs.target_audience,
            "keywords": user_inputs.keywords,
            "platform_params": user_inputs.platform_params
        })

        validation = self.validator.validate_content(
            content=content,
            tone=user_inputs.tone,
            keywords=user_inputs.keywords
        )

        analysis = await self.analyzer.analyze_content(content)

        return ContentOutput(
            content=content,
            validation=validation,
            metadata={
                "task": task,
                "platform": self.config.name,
                "analysis": analysis
            },
            platform_data=user_inputs.platform_params
        )