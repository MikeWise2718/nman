# Purpose
- These specs are for a web-hosted network manager (NMan in the following) that quickly gives me the status of my home network, and allows me to configure certain things.
- It would quickly alerted to network anomilies (nodes, down, services down, unexpected traffic, etc.)

# Audience 
- The audience is me, a sophisticed tech-savy user who wants detailed technical information at a glance

# User stories
- User stories would be the usual about seeing unusual activity indicating a failure or maybe a break-in, attack, or infection.

# Features
- NMan would query various nodes on my home network (for example a Rasbery Pi) to get current and historical information.
- NMan would be able to remotely configure these nodes.
- Initially the Raspberry Pi would
    - Run a process programmed in python.
    - Ping a configuraable list of internal nodes to see if they are up
    - Ping a configuraable list of extenal nodes to see if they are up.
    - The configuration would be centrally managed.
    - This raspbery pi proces would be developed concurently
- NMan would also query Fritzbox routers for status information.
- NMAN would also query one or two managed switches (perhaps over SNMP) to get various statistics.
- NMan should have mutiple display options organized in cards.
- NMan would have an AI summary of what the current stae of the network is

# UI
- It should have an interface looking somewhat like the image in `UiSample.png` in this folder
- It should have status sections in cards, with a vertical main menu on the left
- The order of the cards on the page, and if they are displayed or not should be configurable:
  - moving around with drag-and-drop
  - enable with an "Add Card" main menu item on
  - cards should be "deleteable" with an X icon in the upper right
  - Cards should be "exapandable" to use the entire screen with an appropirate icon in the upper right
- Initially I would like the following cards
  - Network uptime
  - Node reachability (from raspbery Pi)
  - Network Swich traffic

# Architecture
- I would like to host it on a QNAP T453D and have the central manager run there
- The would query various nodes on my home network (for example a Rasbery Pi) to get current and historical information.
- Node list 
   - A Raspberry PI
   - various FritzBoxe Wifif Routers (including at least the 7490)
   - Mikrotik Cloud Router Switch CR5125-24G--15-FIM
   - Various Windows 11 PCs
   - Various Ubunto PCs
   
- The raspbery Pi process would be developed as part of this program
  
# NFR
- Initially this is an exeriement and there is no real need for privacy or security concerns  

# Specifics
- NMAN would be developed on my Windows workstation and pushed periodically to the QNAP.
- It should be written in python 3.13.

# Development
- Development will be manged with the uv package manager
- Specs will be stored in the "specs" folder, including this file
- A readme with the overall purpose and startup instrucations should be created
- Developement will start with PoCs to understand what can be monitored in Fritzbox Routers and our network Switchs

# Misc

the following is embedded here for reference only - these are not instructions or part of the spec

## High-Level Spec Outline for Claude Code Apps
- Section	Description
- Purpose and Objectives : 	Clearly state application goals and how an AI agent will be used??.
- Core User Stories & Scenarios :	Identify main workflows the agent will power; include interaction examples??.
- Key Features & Agent Capabilities	 : List essential functions, distinguishing agent-driven ("skills," automated reasoning) vs. standard logic??.
- Agent Architecture & Skill Design : 	Describe the skill system (prompt templates, context injection, modifiable execution) and plugin structure if relevant?.
- User Experience (UX) Considerations	: Specify desired conversational UX, agent handoff behaviors, and error handling??.
- Integration & Platform Requirements	: Note external API access, CLI usage, supported platforms, and environment specifics?.
- Non-Functional Requirements	: Detail performance, scalability, security, privacy, and compliance needs for both the agent and core system?.
- Success Criteria & Test Plan :	Define what a successful agent feature or workflow looks like, including test-driven development requirements?.
- Development & Agent Operations : 	Outline workflow for updating skills, adding features, and maintaining agent compatibility (e.g., branching, skill updates)??.
- Stakeholders & Maintenance Roles :	Assign roles such as product owner, agent validator, skill designer, and end user??.