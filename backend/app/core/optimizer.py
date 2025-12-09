from app.models.schemas import TaskRequest, OptimizedPrompt
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class PromptOptimizer:
    def __init__(self) -> None:
        self.dspy_available = False
        if settings.USE_REAL_OPTIMIZER:
            try:
                import dspy
                # Assume env vars OPENAI_API_KEY or similar are set for DSPy providers
                # Default to OpenAI for now as a standard example, user can configure dspy settings globally
                dspy.settings.configure(lm=dspy.OpenAI(model='gpt-4o'))
                self.dspy_available = True
                logger.info("Real DSPy optimizer enabled.")
            except ImportError:
                logger.warning("USE_REAL_OPTIMIZER is True but dspy is not installed. Falling back to mock.")
            except Exception as e:
                logger.warning(f"Failed to initialize DSPy: {e}. Falling back to mock.")

    async def optimize(self, task: TaskRequest) -> OptimizedPrompt:
        """
        Takes a raw task request and returns a structured, optimized prompt.
        """
        
        if self.dspy_available:
            return await self._optimize_with_dspy(task)
        
        return self._optimize_mock(task)

    async def _optimize_with_dspy(self, task: TaskRequest) -> OptimizedPrompt:
        import dspy
        
        class OptimizePrompt(dspy.Signature):
            """Refine a raw user task into a precise software engineering prompt for an autonomous agent."""
            raw_description = dspy.InputField(desc="The user's original request")
            context = dspy.InputField(desc="List of relevant files or context")
            constraints = dspy.InputField(desc="Specific constraints")
            
            optimized_prompt = dspy.OutputField(desc="The detailed, step-by-step prompt for the coding agent")
            reasoning = dspy.OutputField(desc="Why this structure was chosen")

        # Basic zero-shot prediction
        predictor = dspy.Predict(OptimizePrompt)
        
        response = predictor(
            raw_description=task.description, 
            context=", ".join(task.context_files),
            constraints=str(task.constraints)
        )
        
        return OptimizedPrompt(
            original_task=task.description,
            optimized_prompt=response.optimized_prompt,
            reasoning=response.reasoning,
            estimated_tokens=len(response.optimized_prompt) // 4
        )

    def _optimize_mock(self, task: TaskRequest) -> OptimizedPrompt:
        # Logic inspired by dspydantic: Structure the intent.
        prompt_structure = f"""
        ROLE: Expert Software Architect & Engineer
        
        TASK: {task.description}
        
        CONTEXT FILES: {', '.join(task.context_files)}
        
        CONSTRAINTS: {task.constraints if task.constraints else "None"}
        
        OBJECTIVE: Execute the task with minimal iterations. Verify all changes.
        """
        
        return OptimizedPrompt(
            original_task=task.description,
            optimized_prompt=prompt_structure.strip(),
            reasoning="[MOCK] Structured the request into ROLE, TASK, CONTEXT, and CONSTRAINTS.",
            estimated_tokens=len(prompt_structure) // 4
        )

optimizer = PromptOptimizer()