'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowRight, Sparkles, Zap, Shield, Layers, CheckCircle2 } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface">
      {/* Navigation */}
      <nav className="border-b border-border bg-surface-light">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Sparkles className="h-6 w-6 text-accent" />
              <span className="text-xl font-semibold text-text-primary">OpenClawAgents</span>
            </div>
            <Link
              href="/dashboard"
              className="px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent-dark transition-colors flex items-center space-x-2"
            >
              <span>Launch Dashboard</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-text-primary mb-6">
            Multi-Agent Content
            <br />
            <span className="text-accent">Research Pipeline</span>
          </h1>
          <p className="text-xl text-text-secondary max-w-2xl mx-auto mb-8">
            Automate your content creation workflow with intelligent AI agents that research, 
            analyze, write, optimize, and validate content in a coordinated pipeline.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-8 py-4 bg-accent text-white rounded-lg text-lg font-medium hover:bg-accent-dark transition-colors space-x-2"
          >
            <span>Get Started</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-surface-light py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-text-primary text-center mb-12">
            Powered by Advanced AI Agents
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<Sparkles className="h-8 w-8" />}
              title="Research Agent"
              description="Gathers information from multiple sources, summarizes findings, and creates comprehensive research reports."
            />
            <FeatureCard
              icon={<Layers className="h-8 w-8" />}
              title="Analyst Agent"
              description="Synthesizes research data, extracts insights, creates structured outlines, and performs fact-checking."
            />
            <FeatureCard
              icon={<Zap className="h-8 w-8" />}
              title="Writer Agent"
              description="Generates high-quality, well-structured content based on research and outlines with professional tone."
            />
            <FeatureCard
              icon={<Shield className="h-8 w-8" />}
              title="SEO Agent"
              description="Optimizes content for search engines with keyword analysis, metadata optimization, and ranking improvements."
            />
            <FeatureCard
              icon={<CheckCircle2 className="h-8 w-8" />}
              title="Quality Agent"
              description="Validates content quality, checks grammar, verifies facts, and ensures publication-ready standards."
            />
            <FeatureCard
              icon={<Layers className="h-8 w-8" />}
              title="Coordinator Agent"
              description="Orchestrates the entire workflow, manages task dependencies, and monitors agent performance."
            />
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-text-primary text-center mb-12">
            Built With Modern Technology
          </h2>
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-semibold text-text-primary mb-6">Backend</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Python 3.9+ with FastAPI</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Groq API (Llama 3.1 & 3.3 Models)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Task Queue & Dependency Management</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Persistent Memory System</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>RESTful API Architecture</span>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="text-2xl font-semibold text-text-primary mb-6">Frontend</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Next.js 14 with TypeScript</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Tailwind CSS for Styling</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>React Hooks & Modern Patterns</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Real-time Status Updates</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                  <span>Responsive Design</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary text-white py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Automate Your Content Pipeline?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Start creating high-quality, SEO-optimized content with our multi-agent system.
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center px-8 py-4 bg-accent text-white rounded-lg text-lg font-medium hover:bg-accent-light transition-colors space-x-2"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-surface-light py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-text-secondary">
          <p>© 2026 OpenClawAgents. Built with ❤️ for intelligent content automation.</p>
        </div>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) {
  return (
    <div className="bg-surface-light border border-border rounded-xl p-6 hover:shadow-lg transition-shadow">
      <div className="text-accent mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-text-primary mb-2">{title}</h3>
      <p className="text-text-secondary">{description}</p>
    </div>
  )
}

