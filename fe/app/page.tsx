import Image from 'next/image'
import Link from 'next/link'
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
            width={75}
            height={25}
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
          <Link href="/dashboard" className={styles.dashboardButton}>Dashboard</Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <div className={styles.badge}>#1 Brand Intelligence Platform</div>
          <h1 className={styles.headline}>
            {/* add a new line after Becomes but before Brand */}
            Where Visibility Becomes <br /> Brand{' '}
            <span className={styles.headlineItalic}>Intelligence</span>
          </h1>
          <p className={styles.description}>
            <em>There&apos;s endless noise about your brand, <br /> but no clear signal of what matters.</em>
          </p>
          <div className={styles.ctaButtons}>
            <Link href="/dashboard" className={styles.primaryButton}>
              Filter Out the Noise →
            </Link>
          </div>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className={styles.trustedBy}>
        <p className={styles.trustedByText}>Trusted By Teams At</p>
        <div className={styles.logos}>
          <div className={styles.logoItem}>None</div>
        </div>
      </section>
    </main>
  )
}

