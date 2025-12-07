import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.hero}>
      <div className={styles.heroContent}>
        <div className={styles.starIcon}>✦</div>
        <Heading as="h1" className={styles.heroTitle}>
          Physical AI &<br />Humanoid Robotics
        </Heading>
        <p className={styles.heroSubtitle}>
          Your journey into embodied artificial intelligence begins here. From fundamental concepts to advanced implementations, explore the technology that's shaping our physical world.
        </p>
        <div className={styles.heroButtons}>
          <Link className={styles.primaryButton} to="/docs">
            Start Learning
          </Link>
          <Link className={styles.secondaryButton} to="/docs/glossary">
            Explore Glossary
          </Link>
        </div>
      </div>
    </header>
  );
}

function FeaturedModules(): ReactNode {
  const modules = [
    {
      title: 'Module 1',
      subtitle: 'Foundations',
      topics: ['Physical AI Basics', 'ROS 2 Architecture', 'Sensors & Actuators'],
      link: '/docs/module-1',
      color: '#00d4ff'
    },
    {
      title: 'Module 2',
      subtitle: 'Perception',
      topics: ['Computer Vision', 'Sensor Fusion', 'SLAM'],
      link: '/docs/module-2',
      color: '#ff6b9d'
    },
    {
      title: 'Module 3',
      subtitle: 'Motion & Control',
      topics: ['Kinematics', 'Path Planning', 'Manipulation'],
      link: '/docs/module-3',
      color: '#c561f6'
    },
    {
      title: 'Module 4',
      subtitle: 'Intelligence',
      topics: ['Machine Learning', 'Reinforcement Learning', 'Integration'],
      link: '/docs/module-4',
      color: '#ffd93d'
    }
  ];

  return (
    <section className={styles.featuredSection}>
      <div className={styles.sectionHeader}>
        <div className={styles.starIcon}>✦</div>
        <Heading as="h2" className={styles.sectionTitle}>
          Featured Modules
        </Heading>
      </div>
      <div className={styles.modulesGrid}>
        {modules.map((module, idx) => (
          <Link key={idx} to={module.link} className={styles.moduleCard}>
            <div className={styles.moduleHeader}>
              <h3 className={styles.moduleTitle}>{module.title}</h3>
              <span className={styles.moduleSubtitle}>{module.subtitle}</span>
            </div>
            <ul className={styles.topicsList}>
              {module.topics.map((topic, i) => (
                <li key={i}>{topic}</li>
              ))}
            </ul>
            <div className={styles.moduleAccent} style={{backgroundColor: module.color}} />
          </Link>
        ))}
      </div>
    </section>
  );
}

function AIAssistantSection(): ReactNode {
  return (
    <section className={styles.aiSection}>
      <div className={styles.aiContent}>
        <div className={styles.starIcon}>✦</div>
        <Heading as="h2" className={styles.aiTitle}>
          Ask the AI Tutor
        </Heading>
        <p className={styles.aiDescription}>
          Get instant answers to your questions about Physical AI concepts, code examples, and implementation details. Our intelligent assistant is trained on the entire textbook.
        </p>
        <div className={styles.aiFeatures}>
          <div className={styles.aiFeature}>
            <span className={styles.aiFeatureIcon}>🤖</span>
            <span>Context-Aware Responses</span>
          </div>
          <div className={styles.aiFeature}>
            <span className={styles.aiFeatureIcon}>📚</span>
            <span>Citation-Backed Answers</span>
          </div>
          <div className={styles.aiFeature}>
            <span className={styles.aiFeatureIcon}>🎯</span>
            <span>Difficulty-Adapted Explanations</span>
          </div>
        </div>
        <p className={styles.aiNote}>
          * AI Assistant available on all chapter pages via the chat widget
        </p>
      </div>
    </section>
  );
}

function KeyTopicsSection(): ReactNode {
  const topics = [
    { emoji: '🤖', label: 'Humanoid Robots', link: '/docs/module-1/week-1-2/1.1-introduction-to-physical-ai' },
    { emoji: '🦾', label: 'Kinematics', link: '/docs/module-3' },
    { emoji: '👁️', label: 'Computer Vision', link: '/docs/module-2' },
    { emoji: '🧠', label: 'Machine Learning', link: '/docs/module-4' },
    { emoji: '🗺️', label: 'SLAM', link: '/docs/module-2' },
    { emoji: '⚙️', label: 'ROS 2', link: '/docs/module-1' },
    { emoji: '📡', label: 'Sensors', link: '/docs/module-1' },
    { emoji: '🎮', label: 'Control Systems', link: '/docs/module-3' }
  ];

  return (
    <section className={styles.topicsSection}>
      <div className={styles.sectionHeader}>
        <Heading as="h3" className={styles.topicsTitle}>
          Key Topics
        </Heading>
        <Link to="/docs/glossary" className={styles.viewAllLink}>
          View All →
        </Link>
      </div>
      <div className={styles.topicsGrid}>
        {topics.map((topic, idx) => (
          <Link key={idx} to={topic.link} className={styles.topicChip}>
            <span className={styles.topicEmoji}>{topic.emoji}</span>
            <span className={styles.topicLabel}>{topic.label}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}

function AboutSection(): ReactNode {
  return (
    <section className={styles.aboutSection}>
      <div className={styles.aboutContent}>
        <Heading as="h3" className={styles.aboutTitle}>About This Textbook</Heading>
        <p className={styles.aboutText}>
          This comprehensive textbook covers the fundamentals and advanced concepts of Physical AI and Humanoid Robotics. 
          Whether you're a student, researcher, or professional, you'll find detailed explanations, practical implementations, 
          and real-world applications across 15 weeks of structured content.
        </p>
        <div className={styles.aboutFeatures}>
          <div className={styles.aboutFeature}>
            <span className={styles.aboutFeatureNumber}>15</span>
            <span className={styles.aboutFeatureLabel}>Weeks of Content</span>
          </div>
          <div className={styles.aboutFeature}>
            <span className={styles.aboutFeatureNumber}>4</span>
            <span className={styles.aboutFeatureLabel}>Core Modules</span>
          </div>
          <div className={styles.aboutFeature}>
            <span className={styles.aboutFeatureNumber}>60+</span>
            <span className={styles.aboutFeatureLabel}>Technical Terms</span>
          </div>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="A comprehensive technical textbook covering Physical AI and Humanoid Robotics concepts, design principles, and practical implementations.">
      <HomepageHeader />
      <main className={styles.mainContent}>
        <FeaturedModules />
        <AIAssistantSection />
        <KeyTopicsSection />
        <AboutSection />
      </main>
    </Layout>
  );
}
