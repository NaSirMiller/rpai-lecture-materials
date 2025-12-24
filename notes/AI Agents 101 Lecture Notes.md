## Outline 
0. Installation & Setup
	- [Link to download Ollama for Linux, Mac, Windows](https://ollama.com/download/windows)
1. Framing & Definitions
	- What are agents? 
	- Examples of agents
	- Why agents?
	- Difference between LLM agents and RL agents
	**Include mention to Claude interview quotes**
2.  Topic Deep-dive
		**Three Big Pillars: Tools, Memory, Planning/Autonomy)
	- Agent loop
		**Emphasize the loop is the primary benefit of agentic applications**
	- Tools
		- What are tools?
		- Benefit of tools rather than LLM generating output through pre-defined knowledge (what the LLM already knows through training)
	- Memory 
		- Scratchpad/Working
			- Ex: Chain of thought steps written down in temporary data structure, i.e. a list
		- Short-term
			- Remains for duration of the user session
			- Ex: A list of user, agent messages
		- Long-term
			- Persistent across sessions
			- Ex: Vector or traditional database
	- Planning
		- ReAct (Reason + Act)
			- Agent alternates between reasoning and acting
			- Simple, yet effective
		- Tree-of-Thought (ToT)
			- Agent explores multiple decision paths (i.e  a tree)
			- If a path "looks weak", the agent backtracks
			- More computationally expensive, but more "powerful"
		- Planner-executor Split
			- Planner creates subgoals from initial macro-goal
			- Executor carries out each subgoal
	- Autonomy
		- Low: Executes one step and stops
		- Medium: Loop until goal is completed
		- High: Create new goals, call APIs
		- Examples:
			- Low: Calculator agent
			- Medium: Research assistant
			- High: AutoGPT
	- Evaluation Methods
		- Self-evaluation
		- LLM as a judge (Critic-actor)
		- Human-in-the loop approval/denial
		- Heuristics
3. Agentic Ecosystem
	**Briefly mention frameworks, so participants understand that these concepts are not framework exclusive**
	- Langchain & Langgraph
	- LlamaIndex
	- CrewAI
	- AutoGen
	- Haystack
4. (Live) Code Extension
	- Participants can extend code further and interact with the agent hands-on

## Definitions
- Agent Loop
	- Observe
			- Agent reviews current state of the available information 
				- User input
				- Memory
				- Tool outputs
				- MCP Resource
		- Decide
			- Given memory and tools, either generate completely new output or rehash information found in memory
			- Which tools to call?
			- Chain tool calls or stop
			- Breakdown query into sub problems, iff necessary
		- Act
			- Execute
				- If rehash: Summarize information found in memory or other static resources
				- If new: Summarize information found from tool outputs
		- Reflect/Learn
			- Update the memory based on previous query and response
		- Repeat
			- Continue "agent loop" until stop condition is met
				- Possible stop conditions:
					- Goal achieved
					- Resource constraint
						- API timeout
						- Lack of LLM tokens
						- Error
- Tool: A method that an LLM can use to fulfill a goal

## In-Depth Notes
- Scratchpad/working memory
	- Leverage when merging data across multiple data sources
	- Only the name and description of each data chunk is provided to the LLM
		- To access a specific data chunk the LLM looks at all names and description pairs and chooses the best option
		- Ex: Langchain tools only provide the name and description to the LLM so it can quickly choose tools. Only then is the functionality provided.
- Chain of thought
	- Prompt engineering technique that enhances LLM output
	- Used for more complex tasks involving multi-step reasoning
	- Guides model through step-by-step reasoning process
	- Emergent ability
	- Behavior is elicited through a single prompt
	**Idea is to make LLM "think out loud"**
- ReAct
	- Combines chain of thought and external tool use
	- After taking an action, the model reevaluates its progress towards the goal and uses its observations to deliver the final answer or inform the next thought. *i.e. make another tool call.*
		- Observations can be from external knowledge sources, *i.e. a vectorstore*, its context memory, *i.e. previously answered questions*.
	- Performance of ReAct based agents is often dependent on the model it uses, *i.e. more robust models can handle more complex tasks*.
	- Multi-agent ReAct frameworks leverage larger, more performant models as the central agent or the brain and smaller models to complete sub tasks.
	- Agent takes an action, observes results of the action, then decides whether to repeat or end loop
		![[ReAct-loop.png]]
- Determining the loop end condition is a very important consideration in building ReAct agents
	- As a fail safe, add a maximum number of loop iterations to avoid endless loops and unresponsive applications
- ReAct prompting is used to to tell model
	- it can loop until tasks is complete
	- what external tools are available
	- to use chain-of-thought reasoning
	- to use scratchpad for chain of thought
- Sequential and uses one LLM
	- Inefficiencies in latency, cost and accuracy
- Tree-of-Thought
	![[tree-of-thoughts-flow.png]]
	- Each step branches into multiple paths
		- Given the paths the agent can backtrack or explore alternate strategies
		- Multiple solutions are considered and discarded if incorrect
		- Four key components
			1. Thought decomposition
				- Problem is split into smaller steps called thoughts
				- Definition of framework
			2. Thought generation
				- Process of generating a thought
				- Approaches
					- Sampling
						- Generating several independent thoughts
						- Can lead to more creative outputs
						- Best used for creative tasks, *i.e. creative writing*
					- Proposing
						- Thoughts are generated sequentially
						- Avoid duplication
						- Best used for logical problem solving
			3. State evaluation
				- After thoughts are generated, each are evaluated to ensure they are contributing to fulfilling the goal
				- Strategies:
					- Value
						- Assign a scalar value, *i.e a rating 1-10*
						- Helps indicate likelihood of leading to a solution
						- Quantitative assessment of each thought's potential
					- Vote
						- Compares different solutions and selects the most promising one
						- Beneficial when dealing with subjective, or hard to identify, *i.e. creative writing or strategic planning*
			4. Search algorithm
				- BFS
					- All potential solutions are considered equally
					- Beneficial for problems where the solution or shortest path is preferred
				- DFS
					- Thorough examination of each path
		![[tot-components-flow.png]]
- Differences between CoT & ToT
	- ToT is preferred in RL scenarios as they require exploration
	- CoT is preferred in problems that require a logical sequence of thoughts
- Planner-Executor Split
	- LLM Compiler Concept
		- Based on traditional computing compilers
		- Components
			- Planner: Builds a DAG showing which tools to call and in what order
			- Task fetching unit: Schedules ready to run tasks
			- Executor: Executes the tools in parallel if possible
		- Improvements
			- 3.7x faster than older approaches like ReAct
			- 6.7x cheaper when using APIs
			- 9% more accurate than ReAct on complex tasks
		![[llm_compiler_flow.png]]
	- ADaPT: As-Needed Decomposition and Planning with Language Models
		- Only decomposes complex tasks into simple subtasks when necessary
		- Components
			- Planner: Generates short, 3-5 step, plans, that are *only* executed when the executor *fails*
				- Larger LLM
			- Controller: Recursive algorithm, that provides a task to the executor and if the executor fails the controller invokes the planner to generate subtasks. This occurs max depth, *m*, times.
			- Executor: Attempts a provided task 
				- Smaller LLM
	- Plan-and-act: Improving Planning of Agent for Long-Horizon Tasks
		- Same architecture as AdaPT
		- Components
			- Planner: Generates a full plan to complete a goal
				- Focused on determining the *what* and *why* of actions in the plan
			- Executor: Translates steps from plan into actions in the environment
				- Does *not* self-access success
		- Re-planning occurs after every step (the executor takes)
		- Highly adaptive and more accurate
		- Increased latency and token consumption
- 12 Factor Agents
	1. Natural Language to Tool Calls
		 - Convert natural language to structured tool calls
	2. **Own your prompts**
		 - Don't outsource your prompt engineering to a framework
	 3. Own your context windows
		 - "To get the best outputs, you need to give them the best inputs"
		 - Creating great context means
			 - Prompts and instructions to give the model
			 - Documents or external data retrieved
			 - Past state, tool calls, results
			 - Past messages or events from related but separate conversations
			 - Instructions about what sorts of structured data to output
		 - Leverages other formats to minimize token usage, *i.e. use YAML or XML rather than JSON within a message*
	4. **Tools are just structured output**
		 - Do not over complicate tools as they are chunks of deterministic code that are easily reproducible and follow the same principles as any other method
		 - You are simply asking the LLM to output JSON so it can be parsed into an object representing those tools
	5. Unify execution state and business state
		- Execution state
			- current step
			- next step
			- waiting status
			- retry counts
		- Business state
			- What has happened in the agent workflow
		- Aim to simplify these processes through unification
	6. Launch/pause/resume with simple APIs
		- Agents and the orchestrating deterministic code should be able to pause an agent when long running operation is needed
	7. Contact humans with tool calls
		 - Format all outputs as JSON
			 - Give specific tags such as
				 - request human input
				 - done for now
	8. **Own your control flow**
		- Benefits
			- Summarization
			- Caching
			- Approval/denial through LLM or human
			- Logging, tracing, & metrics
			- Rate-limiting
	9. Compact errors into context window
		 - When catching errors during flow, format the stacktrace and provide the error back to the LLM
			 - Reduced token usage
		 - Implement error counter to avoid redundant calls for a broken tool
	10. **Small, Focused Agents**
		- Keeps context cleaner
		- Leverages LLMs inherent specialty aptness
		- Easier testing & debugging
	11. Trigger from anywhere, meet users where they are
		- Trigger agents from slack, discord, sms, etc
		- Enable response via same channels
	12. Make your agent a stateless reducer
		- Accumulator is the context window
		- Reducer is an LLM DetermineNextStep + switch statement 
- AutoGPT
	- Automates prompting process
	- Processes tasks and creates AI agents to fulfill 
- Evaluation heuristics
	- Performance & Efficiency
		- Latency/Response Time: Time it takes an agent to respond to a request or complete a task
			- Lower times are better
		- Throughput: The number of tasks or requests an agent can handle within a specified timeframe
			- Higher value corresponds to the agent having the capacity to handle more work
		- Token usage: Number of tokens used in each request or task
		- Cost-per-interaction: Cost associated with each task or interaction
		- Success rate: Percentage of tasks the agent completes within given timeframe
	- Output quality & Accuracy
		- Accuracy: How closely the agent's output aligns with the correct answer or desired outcome
		- Relevance: Checks if agent's response is related to the user's question or task
		- Coherence & fluency: Assessment of how natural, logical, and grammatically correct agent's are
		- Hallucination rate: How often agent creates incorrect or fabricated information
		- Groundedness: Checks whether the agent's responses are based on real, verifiable information -- primarily when using external sources
	- Robustness & reliability
		- Consistency: Agent provides similar, correct answers when given similar or the same questions
		- Error rate: Frequency at which the agent makes mistakes or fails to respond correctly
			- Resilience to adversarial attacks: How well the agent can handle inputs designed to trick the agent or cause it to fail intentionally  
	- Safety & Ethical
		- Bias detection: Identification of unfair treatment towards protected groups
		- Harmful content generation: Frequency at which toxic, offensive, or generated content is generated
	- User-experience
		- CSAT, NPS: Satisfaction with agent's performance
			- Directly gathered from user
		- Turn count: The number of messages it takes for the agent to complete a user's request
	- Task-specific
		- LLM-as-a-judge
			- Evaluates the quality of AI text generation
		- BLEU
			- Measures the amount of shared word sequences between an AI response and references
			- The more shares sequences the better
		- ROUGE
			- How many of the important n-grams in the reference appear in the generated output

## Demo Idea
1. Research agent using wikipedia api
## Demos Needed
1. Showcase memory tiers
	-  ~~Scratchpad
		-  ~~scratchpad object
			-  ~~has list attribute
		- ~~after n messages, the object is reset
	- ~~Short-term
		- ~~Stores messages in a list
			- ~~Overrides on terminal close
	-  ~~Long-term
		- ~~Use FAISS vector store
2. ~~Showcase tool format and use-case
	 - ~~Search what is the status of the "Sudanese civil war"
		 - ~~Recent event that open-source LLM *should not* have knowledge of
		 - ~~Use search tool
3. Showcase agent calling tools & planning/executing

## Participant Exercise
1. Add relevant tools
2. Add llm-as-a-judge or other evaluators

## Resources to Checkout
- [5 Tiers of AI Agents](https://hackernoon.com/the-5-tiers-of-ai-agentsand-how-to-build-each-one)
- [What is a scratchpad?](https://assets-global.website-files.com/6166aaf587246515a48bd298/652dd93ecc56eb3a9ff7ce3f_Prolego_An%20Introduction%20to%20the%20LLM%20Scratchpad%20Design%20Pattern.pdf)
- [What is a ReAct agent?](https://www.ibm.com/think/topics/react-agent)
- [What is chain of thought?](https://www.ibm.com/think/topics/chain-of-thoughts)
- [What is Tree-of-Thoughts?](https://www.ibm.com/think/topics/tree-of-thoughts)
- [Creating 12 factor agents](https://github.com/humanlayer/12-factor-agents?tab=readme-ov-file)
- [Separating AI Agents into Planner and Executor](https://medium.com/@jaouadi.mahdi1/separating-ai-agents-into-planner-and-executor-7705b58d79fd)
- [AI Agent Evaluation Metrics](https://qawerk.com/blog/ai-agent-evaluation-metrics/?utm_source=chatgpt.com)
- [AI Agent Evaluation: Methods, Challenges and Best Practices](https://galileo.ai/blog/ai-agent-evaluation?utm_source=chatgpt.com
- [Mastering Agents: Metrics for Evaluating AI Agents](https://galileo.ai/blog/metrics-for-evaluating-ai-agents?utm_source=chatgpt.com))
- [What is AI Agent Evaluation?](https://www.ibm.com/think/topics/ai-agent-evaluationAD)