from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from content_review_crew.llm import groq_llm


@CrewBase
class ContentReviewCrew:
    """Reviews a text from different angles."""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def clarity_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["clarity_reviewer"],  # type: ignore[index]
            llm=groq_llm(),
            verbose=True,
        )

    @task
    def clarity_review_task(self) -> Task:
        return Task(config=self.tasks_config["clarity_review_task"])  # type: ignore[index]

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
