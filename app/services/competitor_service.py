def competitor_research_guidance() -> str:
    """
    This assignment does not provide a search engine or competitor data API.
    The LLM must label competitor names as suggestions, not verified facts.
    """
    return (
        "Do not claim that competitor details have been independently verified. "
        "Suggest at least three plausible competitors only when there is enough "
        "business context. Mark every competitor as an AI-generated suggestion "
        "and explain that the user should verify it. If uncertain, state that "
        "reliable competitor identification is limited."
    )
