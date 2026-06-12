import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocussaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title" style={{ fontSize: '4rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle" style={{ fontSize: '1.5rem', opacity: 0.7, marginTop: '1rem' }}>
          {siteConfig.tagline}
        </p>
        
        {/* The "3D Glass Card" Feature - Optimized for Project Context */}
        <div className={styles.heroVisual} style={{
          marginTop: '4rem',
          perspective: '1000px',
          display: 'flex',
          justifyContent: 'center'
        }}>
          <div className={styles.glassCard} style={{
            width: '300px',
            height: '200px',
            background: 'rgba(255, 255, 255, 0.4)',
            backdropFilter: 'blur(12px)',
            borderRadius: '24px',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            transform: 'rotateX(10deg) rotateY(-10deg)',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.2rem',
            fontWeight: 'bold',
            color: '#007aff'
          }}>
            <div style={{textAlign: 'center', padding: '0 20px'}}>
              <div style={{fontSize: '3rem', marginBottom: '8px'}}>🚀</div>
              <div style={{fontSize: '1.1rem', lineHeight: '1.4', fontWeight: 700}}>Mastering AI Agents & Coding 101</div>
            </div>
          </div>
        </div>

        <div className={styles.buttons}>
          <Link
            className={clsx('button button--secondary button--lg', styles['button--primary'])}
            to="/docs/intro">
            Get Started — 5min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
