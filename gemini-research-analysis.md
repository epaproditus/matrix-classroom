# **Orchestrating the Digital Frontier: Technical and Pedagogical Analysis of the Matrix-Integrated Instructional System**

The proposed transition of the instructional environment at class.mr-romero.com from a standard chat-based interaction to an automated instructional delivery system represents a significant shift in the application of decentralized protocols to K-12 mathematics. By integrating the Matrix protocol, the Honcho memory layer, and the Texas Education Agency (TEA) Bluebonnet Learning curriculum, this project attempts to encode complex pedagogical routines into an automated orchestration framework. This analysis evaluates the architecture, pedagogical alignment, and strategic potential of this vision, identifying the systemic implications of deploying a "pedagogy-as-protocol" model within a middle school setting.

## **Infrastructure Sovereignty: Matrix as a Decentralized State Machine**

The selection of a self-hosted Matrix homeserver, specifically the Synapse implementation with a PostgreSQL backend, provides a foundation for instructional sovereignty that is absent in centralized, proprietary platforms. Matrix operates not merely as a communication tool but as a decentralized, eventually consistent state machine where homeservers exchange signed JSON events over HTTP.1 This architecture ensures that every instructional event—from a Bell Ringer prompt to a peer discussion—is recorded as a permanent, verifiable, and cryptographically signed entry in the database.

The technical stack utilizes a specific configuration to enforce a "walled garden" necessary for a 7th-grade classroom. The deployment of a custom Synapse module, room\_blocker, is critical for maintaining instructional focus and preventing unauthorized peer-to-peer interactions. This module utilizes the Synapse third-party event rules mechanism to deny event creation under specific conditions, such as students attempting to create their own rooms or initiating direct messages (DMs) outside of authorized bot-mediated channels.2 The technical configuration of the homeserver is summarized in the following table.

| Infrastructure Component | Technology Specification | Instructional and Regulatory Function |
| :---- | :---- | :---- |
| Homeserver Implementation | Matrix Synapse (Python/Twisted) | Manages core room state, message routing, and event resolution.4 |
| Database Layer | PostgreSQL \+ pgvector | Persistent storage for room history and embedding vectors for memory.5 |
| Client Interface | Cinny (Web-based) | Student-facing interface for real-time interaction and content viewing. |
| Security Perimeter | Cloudflare Tunnel | Obfuscates the internal IP and manages TLS termination without open ports.7 |
| Logic/Memory Layer | Honcho (Managed or Self-hosted) | Provides stateful reasoning and persona maintenance across sessions.5 |
| Access Control | Custom room\_blocker Module | Restricts room and community creation to prevent unauthorized student DMs.2 |
| Compliance Status | COPPA-cleared; FERPA in progress | Ensures student data privacy and follows legal mandates for educational data.2 |

The use of end-to-end encryption (E2EE) within this environment introduces significant technical complexity. Because Matrix homeservers see only Megolm ciphertext, the infrastructure provider cannot access message content.1 However, this leads to potential "Unable to Decrypt" (UTD) errors, particularly in large rooms or when session keys are not properly synchronized.9 To mitigate this, the bot runs as a fully isolated Hermes profile (classroom-bot), ensuring that instructional data remains segregated from the teacher’s personal assistant data. This isolation is a critical architectural decision that prevents cross-contamination of student data and teacher-level administrative functions.

## **The Cognitive Memory Layer: Honcho, pgvector, and Formal Logic**

Traditional educational bots often suffer from "semantic drift," where the agent’s understanding of stored knowledge diverges from the actual intent of the interaction.10 The integration of Honcho addresses this by providing a memory system that reasons about data asynchronously in the background.8 Unlike standard Retrieval-Augmented Generation (RAG) which relies on surface-level semantic similarity, Honcho extracts latent information through a formal logical framework.8

This process involves identifying premises, drawing conclusions, and recognizing patterns across multiple interactions to update "peer representations".8 The memory system uses pgvector within the PostgreSQL database to store embedding vectors, which represent the "relatedness" of student discourse.6 The system generates embeddings using models like Cohere v3, allowing for multimodal similarity searches that can include text, images, and audio in a single unified vector space.6

### **The Reasoning Pipeline Mechanics**

The reasoning pipeline in Honcho follows a multi-phase process to ensure cognitive fidelity. When a student interacts with the bot during a "3A Talk" session, the message is enqueued for background processing.8 The system waits until a threshold—approximately 1,000 tokens—is reached before running a "representation task".8 This batching ensures that the reasoning engine has sufficient context to identify meaningful trends.

The extraction of latent information is categorized into four primary reasoning lenses:

* **Deductive Reasoning:** The system identifies explicitly stated content to serve as logical premises and draws certain conclusions from them.8  
* **Inductive Reasoning:** The system recognizes patterns across multiple conclusions or messages, identifying recurring themes or student tendencies.8  
* **Abductive Reasoning:** The system infers the simplest explanations for observed behavior, allowing the bot to hypothesize why a student might be struggling with a specific concept.8  
* **Consolidation:** The system identifies redundant or contradictory information within the student's history to maintain a coherent profile.8

This architectural separation of storage and reasoning ensures that the bot remains a "pedagogical orchestrator" rather than just a "tutor".11 It allows the system to track student understanding against the TEA Bluebonnet Learning curriculum standards in real-time.

## **Pedagogy as Protocol: Encoding the Bluebonnet Learning Model**

The core of the project vision is the translation of the Texas Education Agency’s Bluebonnet Learning curriculum into a series of automated instructional protocols. This curriculum, developed under Texas Education Code Chapter 31, is built on a research-based instructional approach that emphasizes intentional mathematical design and coherence.13 The model is structured around "Learning Together" days, which prioritize collaborative peer discussion, and "Learning Individually" days, which focus on skills practice and independent work.15

The Bluebonnet pedagogical model identifies three distinct phases for every lesson:

* **Before:** Activating prior knowledge and preparing students for the central challenge.13  
* **During:** Engaging in collaborative activity and discourse centered on a specific mathematical problem.13  
* **After:** Reflecting on the process and assessing individual understanding.13

The automated system encodes these phases into Matrix-mediated events. The bot facilitates the "Campus 5-Step Cycle" by posting activity steps from TEA slides, managing timers, and seeding peer responses. Each day’s instruction is based on 12 slides, and the bot delivers verbatim TEA content sourced from facilitation notes.17

### **The Problem-Solving Model**

A central feature of the Bluebonnet curriculum is the Problem-Solving Model Graphic Organizer. This visual tool helps students internalize a consistent approach to mathematical thinking.18 The steps of this model serve as a scaffold for the bot's interaction logic:

1. **Notice and Wonder:** Students identify patterns and initial observations.  
2. **Organize and Mathematize:** Students represent the problem using mathematical symbols or diagrams.  
3. **Predict and Analyze:** Students hypothesize outcomes and evaluate relationships.  
4. **Test and Interpret:** Students execute their plan and verify results.  
5. **Report:** Students share findings and justify their reasoning.18

The bot uses these steps as state triggers. During the "Organize and Mathematize" phase, for example, the bot might provide a structured prompt requiring students to identify known and unknown quantities. The Honcho reasoning engine then analyzes these responses not just for correctness, but for "conceptual accuracy" and the "quality of reasoning".19

## **Instructional Orchestration: The Campus 5-Step Cycle Automation**

The transformation of the "chat app" into an "automated instructional delivery system" is achieved through the systematic automation of the Campus 5-Step Cycle. This cycle ensures that every lesson follows a predictable, research-backed structure.

| Lesson Step | Duration | Bluebonnet Phase | Bot Action in Matrix Environment |
| :---- | :---- | :---- | :---- |
| Step 1: Bell Ringer | 5 Minutes | Before | Posts spiral review question from Skills Practice PDFs in team rooms. |
| Step 2: Hook | 2-5 Minutes | Before | Posts a dramatic question or media provocation to grab attention. |
| Step 3: DI \+ 3A Talk | 15-20 Minutes | During | Posts TEA activity slides \+ "Ask Yourself" prompts with sentence stems. |
| Step 3B: Participation | 5-10 Minutes | During | Runs Lead4Ward strategies (e.g., Four Corners, Card Sort) via polls. |
| Step 4: Practice | 15-20 Minutes | During/After | Assigns Learning Together/Individually problems; tracks student work. |
| Step 5: Closure | Variable | After | Posts Essential Question \+ DMs individual Exit Tickets to each student. |

In Step 3, the "3A Talk" (Direct Instruction with Discourse) is particularly critical. The curriculum requires the teacher to stop every 8 minutes for structured student discourse.17 The bot automates this by posting sentence stems like "I think the trend line will \_\_\_\_\_\_ because \_\_\_\_\_\_".18 These prompts encourage students to externalize their thinking, which research shows improves the quality and coherence of student reasoning.21

The Step 3B "Participation" phase utilizes Lead4Ward strategies designed to increase student movement and engagement. In the digital environment, these are adapted into reaction-based sorting or poll mechanics. For example, the "Four Corners" strategy involves students choosing a response to a question and then "chatting" with partners who made the same choice to justify their thinking.22 The bot facilitates this by creating transient sub-rooms or using Matrix reaction triggers to group students based on their poll responses.

## **Collaborative Dynamics: The Crew as Agentic Personas**

One of the most innovative aspects of the vision is the activation of "The Crew"—Sofia, Marcus, and Jayden—as actual Matrix bot accounts. These fictional peer characters are embedded in the Bluebonnet student edition to model productive struggle and mathematical thinking.13 By giving these characters their own accounts, the system creates a multi-agent social simulation within the classroom rooms.

Research indicates that conversational agents can encourage students to build on others' knowledge when they are perceived as learning partners rather than just experts.24 The Crew personas are programmed to:

* **Model Sentence Stems:** Proactively use "Math Talk" stems to initiate discussions.  
* **Make Intentional Mistakes:** Model the "productive struggle" by posting common misconceptions, allowing human students to correct them and solidify their own understanding.13  
* **Scaffold Discourse:** Act as "less knowledgeable peers" who ask clarifying questions, forcing students to explain their reasoning more deeply.12

This approach aligns with the Vygotskyan concept of the Zone of Proximal Development (ZPD), where the AI agent initiates dialogue and applies adaptive scaffolding informed by the learner's state.12 The "Crew" characters help transition the classroom from a transmissive model of instruction to a dialogic one, where AI serves as a partner in inquiry.21

## **Critical Risks: Technical Debt and Cognitive Erosion**

While the vision is legitimately transformative, several significant risks must be addressed. These challenges range from the technical fragility of self-hosted infrastructure to the potential psychological impacts of AI-mediated learning.

### **Technical Debt and Infrastructure Fragility**

Matrix is a powerful but complex protocol. Maintaining a self-hosted Synapse server requires a dedicated commitment to IT management. Research suggests that the success of such projects often depends on a single person who takes on the role of a "very dedicated IT person" to keep the system running and walk others through fixes when it breaks.25 The potential for "Unable to Decrypt" (UTD) errors and the complexity of managing E2EE keys across multiple student devices can create significant instructional downtime.9

Furthermore, the reliance on LLMs for verifying mathematical accuracy is a major point of failure. While LLMs demonstrate outstanding capabilities in language understanding, they remain weak in symbolic computation and multi-step reasoning.20 In a 7th-grade math context, an AI bot providing an incorrect answer or a faulty justification could significantly undermine student trust and pedagogical consistency.

### **The Risk of "Cognitive Debt"**

A disquieting study from MIT highlights the risk of "Cognitive Debt," where students using AI assistants show a significantly reduced ability to recall their own work.26 The study found that while only 11% of students writing without AI assistance failed to quote their own work, a staggering 83% of those using ChatGPT could not remember a single sentence they had composed minutes before.26 This suggests a "passive approach" to learning where students rely on the AI to do the cognitive heavy lifting, leading to shallow encoding and reduced critical thinking.26 Abraham’s system must be carefully designed to ensure that the AI prompts student effort rather than replacing it.

### **Evaluation of Risks**

The following table summarizes the primary risks identified in the project vision and the associated pedagogical or technical implications.

| Risk Category | Specific Challenge | Pedagogical/Technical Implication |
| :---- | :---- | :---- |
| **Technical Reliability** | E2EE "Unable to Decrypt" (UTD) errors | Instructional downtime and loss of historical context for students.9 |
| **Mathematical Accuracy** | LLM hallucinations in symbolic logic | Misleading feedback on TEKS-aligned math problems.20 |
| **Cognitive Impact** | Accumulation of "Cognitive Debt" | Reduced long-term retention and increased cognitive dependence.26 |
| **Social Dynamics** | "Gaming the System" | Students parroting bot sentence stems without actual conceptual engagement.24 |
| **Governance** | Unmoderated student interaction | Risk of bullying or off-task behavior if Draupnir is not deployed.4 |

## **Emergent Capabilities: Spaced Repetition and Digital Twins**

The most compelling aspect of the vision—the "Structured Pedagogy as Protocol"—unlocks capabilities that the project has not yet fully explored. By encoding the instructional model into a stateful architecture, the system can move beyond daily lesson delivery toward longitudinal student modeling.

### **Forgetting Curves and Personalized Mastery**

A major gap in current LLM-based tutoring is the failure to capture how students' knowledge evolves across their proficiencies and "forgetting patterns".29 Human mastery degrades without practice and consolidates through spaced review.29 By integrating a "temporal forgetting curve" into the Honcho memory layer, the bot could dynamically adjust instruction based on how long it has been since a student last demonstrated mastery of a specific TEKS.29

The bot could automatically insert "Spiral Review" items into the Bell Ringer phase (Step 1\) that are tailored to each student’s specific decay profile. This would transform the system from a task-facilitator into a true Intelligent Tutoring System (ITS) that manages long-term learning trajectories.

### **Async Classroom Replay and the Digital Training Twin**

The ability for absent students to "replay" the lesson cycle async 1:1 with the bot is a profound shift. This effectively creates a "Digital Training Twin" (DTT) of the classroom experience.11 The DTT integrates the learner’s evolving skill state with the pedagogical logic governing the lesson.11 For an absent student, the bot doesn't just provide a transcript; it recreates the *interaction*—the 3A Talk, the Lead4Ward strategy, and the practice phases—ensuring the student experiences the same "productive struggle" as their peers.

## **Strategic Verdict: From "Cool Side Project" to Institutional Tool**

On a scale from "cool side project" to "legitimately transformative educational tool," this project currently lands as a **high-potential prototype**. It is more than a side project because it integrates a rigorous pedagogical model (Bluebonnet/TEKS) with a sophisticated, sovereign technical stack. However, it is not yet "legitimately transformative" due to the high technical debt and the risk of cognitive dependence.

To move to the next tier, the project must demonstrate:

1. **High-Fidelity Math Verification:** Implementing a verification framework (like ValiMath) to ensure LLM feedback is 100% accurate.30  
2. **Longitudinal Stability:** Demonstrating that the system can maintain student state and manage forgetting curves over an entire semester.29  
3. **Human-AI Synergy:** Moving beyond automation to a true partnership where the AI adjusts its behavior based on teacher feedback and the teacher’s timing is informed by AI analytics.31

### **The Bold Idea: The Synthetic Peer Swarm**

To push this vision further, the project could implement a **Synthetic Peer Swarm (SPS)**. Instead of just three fixed "Crew" characters, the system could generate dynamic, transient "peer personas" for each student team. These personas would represent different levels of the ZPD.

In this model, when a student team is working on a problem, the bot inserts a synthetic peer who "thinks" they have the right answer but has a specific, logical misconception (e.g., forgetting to flip the inequality sign when multiplying by a negative). The human students must then "teach" the synthetic peer, correcting the error and justifying their reasoning. This "tutoring-by-teaching" approach is one of the most effective ways to consolidate mathematical understanding.28 This would transform the Matrix rooms into a truly dynamic, interactive laboratory for mathematical thought.

## **Conclusion: The Architecture of Future Learning**

The project vision at class.mr-romero.com represents a sophisticated attempt to reclaim educational technology for the classroom. By moving away from centralized platforms and embracing a "pedagogy-as-protocol" approach, Abraham is building a system that respects both student privacy and research-backed instructional methods. The integration of the Matrix protocol provides the necessary security and sovereignty, while the Honcho memory layer and the Bluebonnet curriculum provide the cognitive and pedagogical depth.

The ultimate success of this vision will depend on the system’s ability to navigate the tension between automation and engagement. The risk of "Cognitive Debt" and the technical challenges of E2EE are significant, but they are not insurmountable. If the system can successfully model student mastery over time and provide a high-fidelity, interactive "Digital Twin" of the classroom experience, it will serve as a model for how AI can truly transform instruction in the state of Texas and beyond. The shift from a "chat platform" to an "automated instructional delivery system" is not just a change in functionality; it is a fundamental reimagining of the digital classroom as a stateful, reasoning-aware participant in the learning process.

#### **Works cited**

1. Building a serverless, post-quantum Matrix homeserver \- The Cloudflare Blog, accessed May 13, 2026, [https://blog.cloudflare.com/serverless-matrix-homeserver-workers/](https://blog.cloudflare.com/serverless-matrix-homeserver-workers/)  
2. Matrix Synapse : how to prevent users from creating rooms or communities \- GitHub Gist, accessed May 13, 2026, [https://gist.github.com/cmuller/518ae8c49c76fb40457ec3065c048b5f](https://gist.github.com/cmuller/518ae8c49c76fb40457ec3065c048b5f)  
3. GitHub \- matrix-org/synapse-user-restrictions: This module allows restricting users from performing actions such as creating rooms or sending invites., accessed May 13, 2026, [https://github.com/matrix-org/synapse-user-restrictions](https://github.com/matrix-org/synapse-user-restrictions)  
4. Matrix & Element: Automating Operations via Secure Messaging | Netscylla's Blog, accessed May 13, 2026, [https://www.netscylla.com/blog/2025/05/16/Matrix-ChatOps.html](https://www.netscylla.com/blog/2025/05/16/Matrix-ChatOps.html)  
5. plastic-labs/honcho: Memory library for building stateful agents \- GitHub, accessed May 13, 2026, [https://github.com/plastic-labs/honcho](https://github.com/plastic-labs/honcho)  
6. A Guide to Embeddings and pgvector \- DEV Community, accessed May 13, 2026, [https://dev.to/googleai/a-guide-to-embeddings-and-pgvector-df0](https://dev.to/googleai/a-guide-to-embeddings-and-pgvector-df0)  
7. How to Install and Create a Chat server using Matrix Synapse and Element on Ubuntu 22.04, accessed May 13, 2026, [https://www.howtoforge.com/how-to-install-and-create-a-chat-server-using-matrix-synapse-and-element-on-ubuntu-22-04/](https://www.howtoforge.com/how-to-install-and-create-a-chat-server-using-matrix-synapse-and-element-on-ubuntu-22-04/)  
8. Honcho Reasoning \- Honcho, accessed May 13, 2026, [https://docs.honcho.dev/v3/documentation/core-concepts/reasoning](https://docs.honcho.dev/v3/documentation/core-concepts/reasoning)  
9. Managing a Public End to End Room on Matrix: Lessons Learned \- Gadgetbridge, accessed May 13, 2026, [https://gadgetbridge.org/blog/managing-a-public-end-to-end-room-on-matrix-lessons-learned/](https://gadgetbridge.org/blog/managing-a-public-end-to-end-room-on-matrix-lessons-learned/)  
10. ByteRover: Agent-Native Memory Through LLM-Curated Hierarchical Context \- arXiv, accessed May 13, 2026, [https://arxiv.org/html/2604.01599v1](https://arxiv.org/html/2604.01599v1)  
11. Development of Digital Training Twins in the Aircraft Maintenance Ecosystem \- MDPI, accessed May 13, 2026, [https://www.mdpi.com/article/10.3390/a18070411?type=check\_update\&version=1](https://www.mdpi.com/article/10.3390/a18070411?type=check_update&version=1)  
12. A Multi-Agent AI Framework for Adaptive and Personalized Learning with Simulated Student Ag \- SciTePress, accessed May 13, 2026, [https://www.scitepress.org/Papers/2026/144189/144189.pdf](https://www.scitepress.org/Papers/2026/144189/144189.pdf)  
13. Volume 1 \- Cloudfront.net, accessed May 13, 2026, [https://d1yqpar94jqbqm.cloudfront.net/documents/BL\_G7\_SE\_Vol\_1.pdf](https://d1yqpar94jqbqm.cloudfront.net/documents/BL_G7_SE_Vol_1.pdf)  
14. AGENDA \- State Board of Education, accessed May 13, 2026, [https://sboe.texas.gov/state-board-of-education/sboe-2026/sboe-2026-january/february2026-sboe-special-called-meeting-agenda.pdf](https://sboe.texas.gov/state-board-of-education/sboe-2026/sboe-2026-january/february2026-sboe-special-called-meeting-agenda.pdf)  
15. Bluebonnet Learning, Geometry \- Instructional Materials Review and Approval (IMRA), accessed May 13, 2026, [https://im.tea.texas.gov/sites/default/files/evaluations/MATHK12\_Bluebonnet%20Learning%2C%20Geometry.pdf](https://im.tea.texas.gov/sites/default/files/evaluations/MATHK12_Bluebonnet%20Learning%2C%20Geometry.pdf)  
16. Texas Education Agency, Open Education Resources, Bluebonnet ..., accessed May 13, 2026, [https://im.tea.texas.gov/sites/default/files/evaluations/Texas%20Education%20Agency%2C%20Open%20Education%20Resources%2C%20Bluebonnet%20Learning%20Grade%206%20Math%2C%20Edition%201.pdf](https://im.tea.texas.gov/sites/default/files/evaluations/Texas%20Education%20Agency%2C%20Open%20Education%20Resources%2C%20Bluebonnet%20Learning%20Grade%206%20Math%2C%20Edition%201.pdf)  
17. Bluebonnet Learning Secondary Mathematics Algebra II | IMRA, accessed May 13, 2026, [https://im.tea.texas.gov/programs/bluebonnet-learning-secondary-mathematics-algebra-ii](https://im.tea.texas.gov/programs/bluebonnet-learning-secondary-mathematics-algebra-ii)  
18. Bluebonnet Learning Problem Solving Posters | Secondary Sentence Stems\! \- TPT, accessed May 13, 2026, [https://www.teacherspayteachers.com/Product/Bluebonnet-Learning-Problem-Solving-Posters-Secondary-Sentence-Stems-13624243](https://www.teacherspayteachers.com/Product/Bluebonnet-Learning-Problem-Solving-Posters-Secondary-Sentence-Stems-13624243)  
19. Conceptual Framework for Pedagogical conversational agents \- ResearchGate, accessed May 13, 2026, [https://www.researchgate.net/figure/Conceptual-Framework-for-Pedagogical-conversational-agents\_fig2\_388054743](https://www.researchgate.net/figure/Conceptual-Framework-for-Pedagogical-conversational-agents_fig2_388054743)  
20. Evaluation of LLMs for mathematical problem solving \- arXiv, accessed May 13, 2026, [https://arxiv.org/html/2506.00309v1](https://arxiv.org/html/2506.00309v1)  
21. Rethinking Think-Pair-Share: Generative AI as a Collaborative Peer in Technology Education \- EdTech Books, accessed May 13, 2026, [https://edtechbooks.org/promptbook/rethinking-think-pair-share](https://edtechbooks.org/promptbook/rethinking-think-pair-share)  
22. instructional \- Thrillshare, accessed May 13, 2026, [https://files-backend.assets.thrillshare.com/documents/asset/uploaded\_file/4880/Seec/64d3f559-f425-4fe7-a7d2-3119997fe670/playlist\_2023\_24.pdf?disposition=inline](https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/4880/Seec/64d3f559-f425-4fe7-a7d2-3119997fe670/playlist_2023_24.pdf?disposition=inline)  
23. Lead Forward Playlist \- Flipbook by LIZ TREVINO \- FlipHTML5, accessed May 13, 2026, [https://fliphtml5.com/iogmx/gvss/Lead\_Forward\_Playlist/](https://fliphtml5.com/iogmx/gvss/Lead_Forward_Playlist/)  
24. Let's teach Kibot: Discovering discussion patterns between student groups and two conversational agent designs | Request PDF \- ResearchGate, accessed May 13, 2026, [https://www.researchgate.net/publication/359844502\_Let's\_teach\_Kibot\_Discovering\_discussion\_patterns\_between\_student\_groups\_and\_two\_conversational\_agent\_designs](https://www.researchgate.net/publication/359844502_Let's_teach_Kibot_Discovering_discussion_patterns_between_student_groups_and_two_conversational_agent_designs)  
25. I wonder why matrix isn't more widerspread at this point. It's open, it's e2ee, ... | Hacker News, accessed May 13, 2026, [https://news.ycombinator.com/item?id=46944528](https://news.ycombinator.com/item?id=46944528)  
26. We Are the 83%, accessed May 13, 2026, [https://www.pragueschool.media/eng-blog-posts/we-are-the-83](https://www.pragueschool.media/eng-blog-posts/we-are-the-83)  
27. Multi-step Problem Solving Through a Verifier: An Empirical Analysis on Model-induced Process Supervision \- ACL Anthology, accessed May 13, 2026, [https://aclanthology.org/2024.findings-emnlp.429.pdf](https://aclanthology.org/2024.findings-emnlp.429.pdf)  
28. Helpful or Harmful? Comparative Study of Perceived and Actual Effectiveness of LLM-Driven Tutors in Game-Based CFL Learning \- MDPI, accessed May 13, 2026, [https://www.mdpi.com/2227-7102/15/11/1502](https://www.mdpi.com/2227-7102/15/11/1502)  
29. Teaching According to Students' Aptitude: Personalized Mathematics Tutoring via Persona-, Memory-, and Forgetting-Aware LLMs \- arXiv, accessed May 13, 2026, [https://arxiv.org/pdf/2511.15163](https://arxiv.org/pdf/2511.15163)  
30. Let's Verify Math Questions Step by Step \- arXiv, accessed May 13, 2026, [https://arxiv.org/html/2505.13903v2](https://arxiv.org/html/2505.13903v2)  
31. Beyond Automation: A Systematic Review of AI Teaching Methodologies and a Framework for Human-AI Synergy in Higher Education \- IEEE Xplore, accessed May 13, 2026, [https://ieeexplore.ieee.org/iel8/6287639/6514899/11443282.pdf](https://ieeexplore.ieee.org/iel8/6287639/6514899/11443282.pdf)  
32. (PDF) Educational chatbots for project-based learning: investigating learning outcomes for a team-based design course \- ResearchGate, accessed May 13, 2026, [https://www.researchgate.net/publication/357044010\_Educational\_chatbots\_for\_project-based\_learning\_investigating\_learning\_outcomes\_for\_a\_team-based\_design\_course](https://www.researchgate.net/publication/357044010_Educational_chatbots_for_project-based_learning_investigating_learning_outcomes_for_a_team-based_design_course)