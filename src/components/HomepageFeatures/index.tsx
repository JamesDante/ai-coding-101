import type {ReactNode} from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './styles.module.css';

type FeatureItem = {
  number: string;
  title: string;
  description: string;
};

const features: {[key: string]: FeatureItem[]} = {
  en: [
    {
      number: '01',
      title: 'From Prompts to Production',
      description:
        '21 chapters from LLM basics and prompt engineering to full-stack AI-assisted development — frontend, backend, database, and testing.',
    },
    {
      number: '02',
      title: 'Build Real AI Agents',
      description:
        'Go beyond chat interfaces. Implement tool calling, MCP integration, multi-agent pipelines, and coding agents that autonomously read, edit, and verify code.',
    },
    {
      number: '03',
      title: 'Ship Production Systems',
      description:
        'Build a SaaS app, an AI chat app, and an agent platform from scratch. Then go deep on RAG, context engineering at scale, and enterprise AI architecture.',
    },
  ],
  'zh-Hans': [
    {
      number: '01',
      title: '从 Prompt 到上线',
      description:
        '21 章内容，涵盖 LLM 基础、提示词工程，到前端、后端、数据库、测试全栈 AI 辅助开发。',
    },
    {
      number: '02',
      title: '构建真实 AI Agent',
      description:
        '超越对话界面。实现工具调用、MCP 集成、多 Agent 流水线，以及能自主读取、编辑、验证代码的编程 Agent。',
    },
    {
      number: '03',
      title: '交付生产级系统',
      description:
        '从零构建 SaaS 应用、AI 聊天应用和 Agent 平台。深入 RAG、大规模上下文工程与企业级 AI 架构。',
    },
  ],
};

function Feature({number, title, description}: FeatureItem) {
  return (
    <div className={styles.featureCard}>
      <span className={styles.featureNumber}>{number}</span>
      <h3 className={styles.featureTitle}>{title}</h3>
      <p className={styles.featureDesc}>{description}</p>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  const {i18n: {currentLocale}} = useDocusaurusContext();
  const list = features[currentLocale] ?? features['en'];

  return (
    <section className={styles.features}>
      <div className={styles.featuresInner}>
        {list.map((item) => (
          <Feature key={item.number} {...item} />
        ))}
      </div>
    </section>
  );
}
