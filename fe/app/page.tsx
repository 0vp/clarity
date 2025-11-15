import Image from 'next/image'
import styles from './page.module.css'

export default function Home() {
  return (
    <main className={styles.main}>
      {/* Background Image */}
      <div className={styles.backgroundContainer}>
        <Image
          src="/flower-field.jpg"
          alt="Hero background"
          fill
          priority
          className={styles.backgroundImage}
        />
      </div>

      {/* Header */}
      <header className={styles.header}>
        <div className={styles.logo}>
          <Image
            src="/logo.png"
            alt="Claro"
            width={150}
            height={50}
            priority
            style={{ objectFit: 'contain', objectPosition: '-3px center' }}
          />
        </div>
        <nav className={styles.nav}>
          <a href="#product">Product</a>
          <a href="#solutions">Solutions</a>
          <a href="#pricing">Pricing</a>
          <a href="#resources">Resources</a>
        </nav>
        <div className={styles.headerActions}>
          <a href="#dashboard" className={styles.dashboardButton}>Dashboard</a>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <div className={styles.badge}>New: Enhanced Workflow Automation</div>
          <h1 className={styles.headline}>
            Find Your Calm in the{' '}
            <span className={styles.headlineItalic}>Complexity</span>
          </h1>
          <p className={styles.description}>
            Our platform handles the intricate data and workflows so you can stop firefighting and start focusing on what matters.
          </p>
          <div className={styles.ctaButtons}>
            <a href="#brands" className={styles.primaryButton}>
              Manage Your Brands →
            </a>
          </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className={styles.trustedBy}>
        <p className={styles.trustedByText}>Trusted By Teams At</p>
        <div className={styles.logos}>
          <div className={styles.logoItem}>Loom</div>
          <div className={styles.logoItem}>Segment</div>
          <div className={styles.logoItem}>Notion</div>
          <div className={styles.logoItem}>Slack</div>
          <div className={styles.logoItem}>Discord</div>
          <div className={styles.logoItem}>Vercel</div>
        </div>
      </section>
    </main>
  )
}

