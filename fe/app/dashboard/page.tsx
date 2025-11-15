import Image from 'next/image'
import Link from 'next/link'
import styles from '../page.module.css'

export default function Dashboard() {
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
          <Link href="/">
            <Image
              src="/logo.png"
              alt="Claro"
              width={150}
              height={50}
              priority
              style={{ objectFit: 'contain', objectPosition: '-3px center' }}
            />
          </Link>
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

      {/* Content Area - Blank for now */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          {/* Blank page content */}
        </div>
      </section>
    </main>
  )
}
