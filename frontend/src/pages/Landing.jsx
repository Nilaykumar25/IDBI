import { Link } from 'react-router-dom'
import { Database, TrendingUp, Shield, Moon, Sun, Layers, Gauge, BarChart3, FileCheck, GitBranch, Eye, Network, ArrowRight, CheckCircle, FileX, Users, Plus, Image, Clock } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'
import { useState, useEffect } from 'react'
import './Landing.css'

// Import team photos (add these after you create the assets folder)
// import nilayPhoto from '../assets/team/nilay.jpg'
// import riddhimaPhoto from '../assets/team/riddhima.jpg'

const Landing = () => {
  const { theme, toggleTheme } = useTheme()
  const [activeSection, setActiveSection] = useState('problem')

  // Track which section is currently in view for active nav link indicator
  useEffect(() => {
    const handleScroll = () => {
      const sections = ['problem', 'what-it-does', 'how-it-works', 'product-preview', 'differentiator', 'team']
      const scrollPosition = window.scrollY + 120 // Offset for header height

      for (let i = sections.length - 1; i >= 0; i--) {
        const section = document.getElementById(sections[i])
        if (section && section.offsetTop <= scrollPosition) {
          setActiveSection(sections[i])
          break
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Initial call
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const features = [
    {
      icon: Database,
      title: 'Alternate Data Aggregation',
      description: 'Pulls GST filings, UPI transaction velocity, Account Aggregator bank statements, and EPFO employment records into a unified credit profile — no traditional credit bureau data required.'
    },
    {
      icon: Layers,
      title: 'Multidimensional Scoring',
      description: 'Composite weighted model tailored by business sector (Trader, Manufacturer, Service Provider) plus machine learning risk classification with SHAP-based explainability for every decision.'
    },
    {
      icon: Eye,
      title: 'Explainable Risk Visualization',
      description: 'SHAP waterfall charts show exactly which factors increased or decreased risk, with directional attribution. Every score comes with plain-language reason codes credit officers can defend.'
    },
    {
      icon: Network,
      title: 'Ecosystem Integration',
      description: 'Built to connect with ULI (Unified Lender Interface), OCEN (Open Credit Enablement Network), and Account Aggregator frameworks for near-real-time assessment at scale.'
    }
  ]

  const problemHighlights = [
    {
      icon: FileX,
      title: 'No bureau history',
      description: 'New-to-Credit MSMEs lack traditional credit artifacts'
    },
    {
      icon: Database,
      title: 'Rich alternate data',
      description: 'GST, UPI, AA, and EPFO data goes unused in decisions'
    },
    {
      icon: Users,
      title: 'Widening credit gap',
      description: 'Viable businesses excluded from formal lending'
    }
  ]

  const workflowSteps = [
    {
      step: '01',
      icon: Database,
      title: 'Connect Data Sources',
      description: 'Consent-based adapters fetch GST return filings, UPI transaction histories, Account Aggregator bank statements, and EPFO contribution records for the MSME.',
      tags: ['GST', 'UPI', 'AA', 'EPFO']
    },
    {
      step: '02',
      icon: BarChart3,
      title: 'Compute Score + Risk Classification',
      description: 'Composite weighted model generates a 0–100 financial health score. ML classifier assigns Low/Medium/High risk band. SHAP explainer identifies top contributing factors.',
      tags: []
    },
    {
      step: '03',
      icon: FileCheck,
      title: 'Issue Assessment + Recommendations',
      description: 'Risk band, confidence scores, six-dimension breakdown, and prioritized improvement recommendations delivered to lender. Ready for underwriting or lender-matching workflows.',
      tags: []
    }
  ]

  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="header-brand">
          <div className="brand-logo">
            <BarChart3 size={24} strokeWidth={2.5} />
          </div>
          <div className="brand-info">
            <span className="brand-name">CreditLine</span>
            <span className="brand-tagline">MSME FINANCIAL HEALTH SCORE</span>
          </div>
        </div>
        <nav className="header-nav">
          <a href="#problem" className={`nav-link ${activeSection === 'problem' ? 'active' : ''}`}>The Problem</a>
          <a href="#what-it-does" className={`nav-link ${activeSection === 'what-it-does' ? 'active' : ''}`}>What It Does</a>
          <a href="#how-it-works" className={`nav-link ${activeSection === 'how-it-works' ? 'active' : ''}`}>How It Works</a>
          <a href="#product-preview" className={`nav-link ${activeSection === 'product-preview' ? 'active' : ''}`}>Product Preview</a>
          <a href="#differentiator" className={`nav-link ${activeSection === 'differentiator' ? 'active' : ''}`}>Differentiator</a>
          <a href="#team" className={`nav-link ${activeSection === 'team' ? 'active' : ''}`}>Team</a>
        </nav>
        <div className="header-actions">
          <button 
            onClick={toggleTheme} 
            className="theme-toggle"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <Link to="/login" className="btn-sign-in">Sign In</Link>
          <Link to="/signup" className="btn-demo">Try Demo</Link>
        </div>
      </header>

      <main className="landing-main">
        {/* Hero Section */}
        <section className="landing-hero">
          <div className="hero-content">
            <div className="hero-eyebrow">MSME Financial Health Score</div>
            <h1 className="hero-headline">
              Closing the MSME <br/>Credit Gap with <span className="headline-accent">Alternate Data</span>
            </h1>
            <p className="hero-description">
              Traditional credit scoring leaves 63 million MSMEs underserved. CreditLine changes that with transparent, explainable credit assessment powered by GST filings, UPI transactions, Account Aggregator data, and EPFO employment records.
            </p>
            <div className="hero-actions">
              <Link to="/signup" className="btn btn-primary">
                Get Started
              </Link>
              <Link to="/login" className="btn btn-secondary">
                View Live Demo
              </Link>
            </div>
          </div>

          <aside className="hero-demo">
            <div className="demo-card">
              <div className="demo-header">
                <span className="demo-label">SAMPLE ASSESSMENT CARD</span>
              </div>
              <div className="demo-business">
                <div className="business-name">Sundaram Textiles Pvt Ltd</div>
                <div className="business-id">GSTIN 27AABCD1234F1Z5</div>
              </div>
              <div className="demo-score">
                <div className="score-gauge">
                  <svg width="140" height="140" viewBox="0 0 140 140">
                    <circle cx="70" cy="70" r="60" fill="none" stroke="var(--divider)" strokeWidth="10"/>
                    <circle cx="70" cy="70" r="60" fill="none" stroke="#1F9D6D" strokeWidth="10"
                      strokeDasharray="377" strokeDashoffset="94" strokeLinecap="round"
                      transform="rotate(-90 70 70)"/>
                    <text x="70" y="68" textAnchor="middle" fontSize="32" fontWeight="700" fill="var(--text-primary)">76</text>
                    <text x="70" y="85" textAnchor="middle" fontSize="11" fill="var(--text-secondary)">HEALTH SCORE</text>
                  </svg>
                </div>
                <div className="score-badge risk-low">LOW RISK</div>
              </div>
              <div className="demo-metrics">
                <div className="metric-row">
                  <span className="metric-label">Revenue Stability</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '78%'}}></div></div>
                  <span className="metric-value">78</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Transaction Velocity</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '82%'}}></div></div>
                  <span className="metric-value">82</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Liquidity Ratio</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '65%'}}></div></div>
                  <span className="metric-value">65</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Employment Consistency</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '85%'}}></div></div>
                  <span className="metric-value">85</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Compliance Score</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '92%'}}></div></div>
                  <span className="metric-value">92</span>
                </div>
                <div className="metric-row">
                  <span className="metric-label">Growth Indicator</span>
                  <div className="metric-bar"><div className="metric-fill" style={{width: '70%'}}></div></div>
                  <span className="metric-value">70</span>
                </div>
              </div>
              <div className="demo-sources">
                <span className="source-badge">● GST LIVE</span>
                <span className="source-badge">● UPI LIVE</span>
                <span className="source-badge">● AA LIVE</span>
                <span className="source-badge">● EPFO LIVE</span>
              </div>
            </div>
          </aside>
        </section>

        {/* Problem Section */}
        <section id="problem" className="landing-section problem-section">
          <div className="section-eyebrow">THE PROBLEM</div>
          <h2 className="section-title">
            New-to-Credit and New-to-Bank MSMEs are often rejected by traditional lenders — despite being creditworthy
          </h2>
          <div className="problem-highlights">
            {problemHighlights.map((item, index) => {
              const Icon = item.icon
              return (
                <div key={index} className="problem-highlight-item">
                  <div className="problem-highlight-icon">
                    <Icon size={22} />
                  </div>
                  <h3 className="problem-highlight-title">{item.title}</h3>
                  <p className="problem-highlight-text">{item.description}</p>
                </div>
              )
            })}
          </div>
          <blockquote className="problem-callout">
            Millions of viable MSMEs generate rich alternate data every day — yet remain invisible to traditional credit models.
          </blockquote>
          <div className="problem-statement">
            <p>
              Traditional lending relies on credit bureau scores, audited financials, and collateral documentation. But millions of viable MSMEs lack these artifacts simply because they're new to formal banking, operate primarily in cash, or haven't yet built a credit history with traditional institutions.
            </p>
            <p>
              Yet these same businesses generate rich alternate data every day: GST return filings that reveal revenue patterns, UPI transactions that show payment velocity, Account Aggregator-permissioned bank statements that demonstrate cash flow discipline, and EPFO records that track employment stability. This data exists — but goes unused in credit decisions.
            </p>
            <p>
              The result: creditworthy MSMEs are excluded from formal credit, lenders miss viable lending opportunities, and the MSME credit gap widens.
            </p>
          </div>
        </section>

        {/* Product Preview Screenshot */}
        <section className="landing-section preview-section">
          <div className="section-eyebrow">THE PRODUCT</div>
          <h2 className="section-title">A complete financial health assessment in one view</h2>
          <div className="preview-image-container">
            <div className="preview-mockup">
              <div className="mockup-header">
                <span className="mockup-title">Credit Assessment Report</span>
                <span className="mockup-file">File No: MSME-2024-001</span>
              </div>
              <div className="mockup-body">
                <div className="mockup-left">
                  <div className="mockup-score-label">Financial Health Score</div>
                  <div className="mockup-score-value">76.0</div>
                  <div className="mockup-score-gauge"></div>
                </div>
                <div className="mockup-right">
                  <div className="mockup-stamp">
                    <div className="stamp-text">LOW</div>
                    <div className="stamp-sub">RISK</div>
                  </div>
                </div>
              </div>
              <div className="mockup-metrics">
                <div className="mockup-metric">
                  <div className="mockup-metric-bar" style={{width: '78%'}}></div>
                </div>
                <div className="mockup-metric">
                  <div className="mockup-metric-bar" style={{width: '65%'}}></div>
                </div>
                <div className="mockup-metric">
                  <div className="mockup-metric-bar" style={{width: '92%'}}></div>
                </div>
              </div>
            </div>
            <p className="preview-caption">
              Score Card view: 0–100 health score, risk band classification, six-dimension breakdown, and ML confidence distribution
            </p>
          </div>
        </section>

        {/* What It Does - Four Pillars */}
        <section id="what-it-does" className="landing-section features-section">
          <div className="section-eyebrow">WHAT IT DOES</div>
          <h2 className="section-title">Four pillars of alternate-data credit assessment</h2>
          <div className="features-grid">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="feature-card">
                  <div className="feature-icon">
                    <Icon size={24} />
                  </div>
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </section>

        {/* How It Works - Expanded */}
        <section id="how-it-works" className="landing-section workflow-section">
          <div className="section-eyebrow">HOW IT WORKS</div>
          <h2 className="section-title">
            From consented data to decision-ready assessment — in three steps
          </h2>
          <div className="workflow-grid">
            {workflowSteps.map((step, index) => {
              const Icon = step.icon
              return (
                <div key={index} className="workflow-item">
                  <div className="workflow-header">
                    <div className="workflow-icon">
                      <Icon size={24} />
                    </div>
                    <span className="workflow-step">{step.step}</span>
                  </div>
                  <h3 className="workflow-title">{step.title}</h3>
                  <p className="workflow-description">{step.description}</p>
                  {step.tags.length > 0 && (
                    <div className="workflow-tags">
                      {step.tags.map((tag, i) => (
                        <span key={i} className="workflow-tag">{tag}</span>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </section>

        {/* Ecosystem Integration Section */}
        <section className="landing-section ecosystem-section">
          <div className="section-eyebrow">ECOSYSTEM INTEGRATION</div>
          <h2 className="section-title">
            Built for the Credit Ecosystem
          </h2>
          <p className="ecosystem-intro">
            Beyond aggregating GST, UPI, Account Aggregator, and EPFO data, the platform publishes computed scores to ULI (Unified Lending Interface) and matches MSMEs to lenders via OCEN (Open Credit Enablement Network) based on their risk band — enabling near-real-time credit assessment instead of manual multi-week underwriting.
          </p>
          <div className="ecosystem-flow">
            <div className="ecosystem-card">
              <div className="ecosystem-icon">
                <BarChart3 size={28} />
              </div>
              <h3 className="ecosystem-card-title">Score Computed</h3>
              <p className="ecosystem-card-text">
                Composite weighted model + ML classifier generate 0–100 health score and Low/Medium/High risk band
              </p>
            </div>
            <div className="ecosystem-arrow">
              <ArrowRight size={32} />
            </div>
            <div className="ecosystem-card">
              <div className="ecosystem-icon">
                <Network size={28} />
              </div>
              <h3 className="ecosystem-card-title">Published to ULI</h3>
              <p className="ecosystem-card-text">
                Score and risk band transmitted to Unified Lending Interface for lender access
              </p>
            </div>
            <div className="ecosystem-arrow">
              <ArrowRight size={32} />
            </div>
            <div className="ecosystem-card">
              <div className="ecosystem-icon">
                <CheckCircle size={28} />
              </div>
              <h3 className="ecosystem-card-title">Matched via OCEN</h3>
              <p className="ecosystem-card-text">
                MSMEs matched to appropriate lenders through Open Credit Enablement Network based on risk profile
              </p>
            </div>
          </div>
        </section>

        {/* Impact Stats Section */}
        <section className="landing-section impact-section">
          <div className="impact-grid">
            <div className="impact-stat">
              <div className="impact-number">4</div>
              <div className="impact-label">Alternate Data Sources</div>
            </div>
            <div className="impact-stat">
              <div className="impact-number">6</div>
              <div className="impact-label">Dimension Scoring Model</div>
            </div>
            <div className="impact-stat">
              <div className="impact-number">3</div>
              <div className="impact-label">Risk Classification Bands</div>
            </div>
            <div className="impact-stat">
              <div className="impact-number">100%</div>
              <div className="impact-label">Explainable by Design</div>
            </div>
          </div>
        </section>

        {/* Product Preview Section */}
        <section id="product-preview" className="landing-section product-preview-section">
          <div className="section-eyebrow">PRODUCT PREVIEW</div>
          <h2 className="section-title">See the Financial Health Card in action</h2>
          <p className="preview-subtitle">
            A live look at the Credit Officer dashboard, powered by real alternate-data scoring
          </p>
          
          <div className="preview-screenshots-grid">
            <div className="screenshot-item">
              <div className="screenshot-frame">
                <div className="browser-chrome">
                  <div className="chrome-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="screenshot-placeholder">
                  <Image size={48} strokeWidth={1.5} />
                </div>
              </div>
              <div className="screenshot-caption">
                <strong>Overview</strong>
                <p>Financial Health Score, Risk Band, and ML confidence breakdown at a glance</p>
              </div>
            </div>

            <div className="screenshot-item">
              <div className="screenshot-frame">
                <div className="browser-chrome">
                  <div className="chrome-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="screenshot-placeholder">
                  <Image size={48} strokeWidth={1.5} />
                </div>
              </div>
              <div className="screenshot-caption">
                <strong>Risk Factors</strong>
                <p>SHAP-driven explanations show exactly why a score landed where it did</p>
              </div>
            </div>

            <div className="screenshot-item">
              <div className="screenshot-frame">
                <div className="browser-chrome">
                  <div className="chrome-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
                <div className="screenshot-placeholder">
                  <Image size={48} strokeWidth={1.5} />
                </div>
              </div>
              <div className="screenshot-caption">
                <strong>Scenario Analysis</strong>
                <p>The What-If Simulator models how specific improvements move the score</p>
              </div>
            </div>
          </div>
        </section>

        {/* Dual-Layer Scoring Differentiator Section */}
        <section id="differentiator" className="landing-section differentiator-section">
          <div className="section-eyebrow">OUR DIFFERENTIATOR</div>
          <h2 className="section-title">Two models, one score, full transparency</h2>
          <p className="differentiator-subtitle">
            Most credit tools force a choice between explainability and accuracy. CreditLine runs both together.
          </p>

          <div className="models-comparison">
            <div className="model-card">
              <div className="model-icon">
                <FileCheck size={32} />
              </div>
              <h3 className="model-title">Rule-Based Composite Model</h3>
              <p className="model-description">
                Fully transparent, auditable. Every point traces to a specific weighted dimension.
              </p>
            </div>

            <div className="models-connector">
              <Plus size={32} strokeWidth={2.5} />
            </div>

            <div className="model-card">
              <div className="model-icon">
                <GitBranch size={32} />
              </div>
              <h3 className="model-title">ML Risk Classifier</h3>
              <p className="model-description">
                Catches non-linear risk patterns a fixed formula would miss.
              </p>
            </div>
          </div>

          <div className="differentiator-callout">
            <p>
              When the two disagree, that divergence itself becomes a signal, flagging the case for manual review instead of silently picking one answer.
            </p>
          </div>
        </section>

        {/* Impact Numbers Section */}
        <section className="landing-section impact-numbers-section">
          <div className="impact-numbers-grid">
            <div className="impact-stat-item">
              <div className="impact-stat-number">63M+</div>
              <div className="impact-stat-label">MSMEs underserved by traditional credit scoring</div>
            </div>
            <div className="impact-stat-item">
              <div className="impact-stat-number">4</div>
              <div className="impact-stat-label">Alternate data sources aggregated</div>
            </div>
            <div className="impact-stat-item">
              <div className="impact-stat-number">6</div>
              <div className="impact-stat-label">Financial health dimensions scored</div>
            </div>
            <div className="impact-stat-item">
              <div className="impact-stat-number">
                <Clock size={48} strokeWidth={2} />
              </div>
              <div className="impact-stat-label">Minutes, not days, per assessment</div>
            </div>
          </div>
        </section>

        {/* Team Section */}
        <section id="team" className="landing-section team-section">
          <div className="section-eyebrow">THE TEAM</div>
          <h2 className="section-title">Built by Team Serendipity</h2>
          
          <div className="team-grid">
            <div className="team-member-card">
              <div className="member-avatar">
                {/* Uncomment and use image once you add the photo to src/assets/team/ */}
                {/* <img src={nilayPhoto} alt="Nilay Kumar" /> */}
                <Users size={40} />
              </div>
              <h3 className="member-name">Nilay Kumar</h3>
              <p className="member-role">AI/ML & Full-Stack Development</p>
            </div>

            <div className="team-member-card">
              <div className="member-avatar">
                {/* Uncomment and use image once you add the photo to src/assets/team/ */}
                {/* <img src={riddhimaPhoto} alt="Riddhima Chaturvedi" /> */}
                <Users size={40} />
              </div>
              <h3 className="member-name">Riddhima Chaturvedi</h3>
              <p className="member-role">AI/ML & Full-Stack Development</p>
            </div>
          </div>
        </section>

        {/* Final CTA Section with Forest Green Background */}
        <section className="landing-section final-cta-section">
          <h2 className="final-cta-title">Ready to close the credit gap?</h2>
          <p className="final-cta-description">
            Try the live demo and see how alternate data changes the lending decision.
          </p>
          <Link to="/signup" className="btn btn-final-cta">
            Try Demo
          </Link>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <div className="brand-logo-small">
              <BarChart3 size={20} strokeWidth={2.5} />
            </div>
            <div className="brand-info-small">
              <span className="brand-name-small">CreditLine</span>
              <span className="brand-tagline-small">MSME FINANCIAL HEALTH SCORE</span>
            </div>
          </div>
          <div className="footer-meta">
            <p className="footer-team">Team Serendipity</p>
            <p className="footer-hackathon">IDBI Innovate Hackathon 2026</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Landing
