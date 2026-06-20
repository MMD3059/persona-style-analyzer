from openai import OpenAI
from app import config


class FanarClient:
    """OpenAI-compatible client for Fanar API."""

    def __init__(self):
        if not config.FANAR_API_KEY:
            raise ValueError(
                "FANAR_API_KEY is not set. "
                "Set it in .env or as an environment variable."
            )
        self.client = OpenAI(
            base_url=config.FANAR_API_BASE,
            api_key=config.FANAR_API_KEY,
        )
        self.model = config.FANAR_MODEL

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_tokens: int = 1500,
        temperature: float = 0.3,
    ) -> str:
        """Send a text generation request to Fanar."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def generate_structured(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        """Generate with lower temperature for structured output."""
        return self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=2000,
        )

    def embed(self, text: str) -> list[float]:
        """Get embeddings from Fanar.

        Note: Fanar API does not currently expose an embeddings endpoint
        natively. This method uses the chat endpoint with a structured
        extraction prompt as a fallback embedding approach.
        If a dedicated embeddings endpoint becomes available, swap this.
        """
        prompt = (
            f"Analyze the following Arabic text and return a numerical "
            f"vector representation capturing its style, tone, and semantics. "
            f"Return exactly 10 comma-separated numbers between -1 and 1:\n\n{text}"
        )
        response = self.generate(
            prompt=prompt,
            temperature=0.1,
            max_tokens=200,
        )
        nums = []
        for token in response.replace("[", "").replace("]", "").split(","):
            try:
                nums.append(float(token.strip()))
            except ValueError:
                continue
        # Pad to 10 dims if needed
        while len(nums) < 10:
            nums.append(0.0)
        return nums[:10]
