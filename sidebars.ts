import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Fundamentals',
      items: [
        'fundamentals/introduction-to-ai-coding',
        'fundamentals/how-llms-understand-code',
        'fundamentals/ai-coding-workflow',
      ],
    },

    {
      type: 'category',
      label: 'Prompt Engineering',
      items: [
        'prompt-engineering/prompting-basics',
        'prompt-engineering/structured-prompts',
        'prompt-engineering/task-decomposition',
      ],
    },

    {
      type: 'category',
      label: 'AI Agents',
      items: [
        'agents/tool-calling',
        'agents/mcp',
        'agents/multi-agent',
        'agents/coding-agent',
      ],
    },

    {
      type: 'category',
      label: 'Projects',
      items: [
        'projects/saas-platform',
        'projects/chat-app',
        'projects/agent-platform',
      ],
    },

    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/context-engineering',
        'advanced/rag',
        'advanced/enterprise-ai',
      ],
    },
  ],
};

export default sidebars;
