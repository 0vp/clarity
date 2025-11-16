'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { fetchBrandsWithStats, type Brand, type BrandStats, initiateSearch, getSearchStatus } from '@/lib/api'
import { Search, Plus, TrendingUp, Clock, RefreshCw, AlertCircle, Loader2, Check, XCircle } from 'lucide-react'

export const dynamic = 'force-dynamic'

type BrandWithStats = Brand & { stats?: BrandStats }

interface InProgressScrape {
  searchId: string
  sources: string[]
  status: 'scraping' | 'completed' | 'failed'
  scrapingStatus: Record<string, string>
  progress: { completed: number; total: number }
  startedAt: number
  error?: string
}

const AVAILABLE_SOURCES = ['trustpilot', 'yelp', 'google_reviews', 'news', 'blog', 'forum', 'website']
const SCRAPING_STORAGE_KEY = 'clarity_scraping'

export default function Dashboard() {
  const router = useRouter()
  const [brands, setBrands] = useState<BrandWithStats[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Add brand form state
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [brandName, setBrandName] = useState('')
  const [website, setWebsite] = useState('')
  const [selectedSources, setSelectedSources] = useState<string[]>(AVAILABLE_SOURCES.filter(s => s !== 'website'))
  const [formError, setFormError] = useState<string | null>(null)
  
  // In-progress scraping state
  const [inProgressScrapes, setInProgressScrapes] = useState<Record<string, InProgressScrape>>({})

  const loadBrands = async () => {
    // Only run in browser environment
    if (typeof window === 'undefined') return
    
    try {
      setLoading(true)
      setError(null)
      const data = await fetchBrandsWithStats()
      setBrands(data)
    } catch (err) {
      console.error('Error loading brands:', err)
      const errorMessage = err instanceof Error ? err.message : 'Failed to load brands'
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  // Load in-progress scrapes from localStorage on mount
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    try {
      const stored = localStorage.getItem(SCRAPING_STORAGE_KEY)
      if (stored) {
        setInProgressScrapes(JSON.parse(stored))
      }
    } catch (err) {
      console.error('Error loading in-progress scrapes:', err)
    }
  }, [])

  // Save in-progress scrapes to localStorage whenever they change
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    try {
      localStorage.setItem(SCRAPING_STORAGE_KEY, JSON.stringify(inProgressScrapes))
    } catch (err) {
      console.error('Error saving in-progress scrapes:', err)
    }
  }, [inProgressScrapes])

  // Poll for scraping status of each in-progress scrape
  useEffect(() => {
    const inProgressBrands = Object.entries(inProgressScrapes).filter(
      ([_, scrape]) => scrape.status === 'scraping'
    )

    if (inProgressBrands.length === 0) return

    const interval = setInterval(async () => {
      for (const [brandName, scrape] of inProgressBrands) {
        try {
          const status = await getSearchStatus(scrape.searchId)

          setInProgressScrapes(prev => {
            const updated = { ...prev }

            if (status.progress?.sources) {
              updated[brandName] = {
                ...updated[brandName],
                scrapingStatus: status.progress.sources,
                progress: {
                  completed: status.progress.completed,
                  total: status.progress.total
                }
              }
            }

            if (status.status === 'completed') {
              updated[brandName].status = 'completed'
              // Reload brands to show completed scrape
              loadBrands()
            } else if (status.status === 'failed') {
              updated[brandName].status = 'failed'
              updated[brandName].error = status.error || 'Scraping failed'
            }

            return updated
          })
        } catch (err) {
          console.error(`Error polling for ${brandName}:`, err)
        }
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [inProgressScrapes])

  const handleStartScraping = async () => {
    if (!brandName.trim()) {
      setFormError('Brand name is required')
      return
    }
    
    try {
      setFormError(null)
      
      // Initialize status for all selected sources
      const initialStatus: Record<string, string> = {}
      selectedSources.forEach(source => {
        initialStatus[source] = 'pending'
      })
      
      const response = await initiateSearch(brandName, selectedSources, website || undefined)
      
      // Add to in-progress scrapes
      setInProgressScrapes(prev => ({
        ...prev,
        [brandName]: {
          searchId: response.search_id,
          sources: selectedSources,
          status: 'scraping',
          scrapingStatus: initialStatus,
          progress: { completed: 0, total: selectedSources.length },
          startedAt: Date.now()
        }
      }))
      
      // Close dialog
      setShowAddDialog(false)
      
      // Reset form
      setBrandName('')
      setWebsite('')
      setSelectedSources(AVAILABLE_SOURCES.filter(s => s !== 'website'))
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to start scraping')
      console.error('Error starting scraping:', err)
    }
  }

  useEffect(() => {
    loadBrands()
  }, [])

  const filteredBrands = brands.filter(brand =>
    brand.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const scrapingBrands = Object.entries(inProgressScrapes).filter(([_, scrape]) =>
    scrape.status === 'scraping'
  )

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    const now = new Date()
    const diffInMs = now.getTime() - date.getTime()
    const diffInSeconds = Math.floor(diffInMs / 1000)
    const diffInMinutes = Math.floor(diffInSeconds / 60)
    const diffInHours = Math.floor(diffInMinutes / 60)
    const diffInDays = Math.floor(diffInHours / 24)
    
    // Less than 1 minute
    if (diffInSeconds < 60) {
      return diffInSeconds <= 1 ? '1 second ago' : `${diffInSeconds} seconds ago`
    }
    
    // Less than 1 hour
    if (diffInMinutes < 60) {
      return diffInMinutes === 1 ? '1 minute ago' : `${diffInMinutes} minutes ago`
    }
    
    // Less than 24 hours
    if (diffInHours < 24) {
      return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`
    }
    
    // Less than 7 days
    if (diffInDays < 7) {
      return diffInDays === 1 ? '1 day ago' : `${diffInDays} days ago`
    }
    
    // More than 7 days - show the actual date
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/">
            <Image
              src="/logo.png"
              alt="Clarity"
              width={75}
              height={25}
              priority
              style={{ objectFit: 'contain', objectPosition: '-3px center' }}
            />
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/dashboard" className="text-sm font-medium text-foreground">
              Dashboard
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Brand Dashboard</h1>
          <p className="text-muted-foreground">Monitor and manage your tracked brands</p>
        </div>

        {/* Search and Add Section */}
        <div className="flex items-center gap-4 mb-6">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search brands..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Brand
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Add New Brand</DialogTitle>
                <DialogDescription>
                  Enter brand details and select sources to scrape.
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4 py-4">
                <div>
                  <label className="text-sm font-medium">Brand Name *</label>
                  <Input
                    placeholder="Nike"
                    value={brandName}
                    onChange={(e) => setBrandName(e.target.value)}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium">Website (Optional)</label>
                  <Input
                    placeholder="https://example.com"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    className="mt-1"
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Sources to Scrape</label>
                  <div className="space-y-2">
                    {AVAILABLE_SOURCES.map(source => (
                      <label key={source} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={selectedSources.includes(source)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedSources([...selectedSources, source])
                            } else {
                              setSelectedSources(selectedSources.filter(s => s !== source))
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm capitalize">{source.replace(/_/g, ' ')}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {formError && (
                  <div className="flex gap-2 items-start text-sm text-destructive bg-destructive/10 p-3 rounded">
                    <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span>{formError}</span>
                  </div>
                )}
                
                <Button onClick={handleStartScraping} className="w-full">
                  Start Scraping
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Loading brands...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                Failed to Load Brands
              </CardTitle>
              <CardDescription>
                {error}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-sm text-muted-foreground">
                  <p className="mb-2">Possible issues:</p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Backend API is not running (should be at http://127.0.0.1:8000)</li>
                    <li>CORS configuration issue</li>
                    <li>Network connectivity problem</li>
                  </ul>
                </div>
                <Button onClick={loadBrands} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Brand Grid */}
        {!loading && !error && (
          <>
            {filteredBrands.length === 0 && scrapingBrands.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-muted-foreground">
                    {searchQuery ? 'No brands found matching your search.' : 'No brands tracked yet. Add one to get started!'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {/* Scraping Brands Cards */}
                {scrapingBrands.map(([scrapingBrandName, scrape]) => (
                  <Card key={scrapingBrandName} className="border-primary/50 h-full">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <CardTitle className="text-xl">{scrapingBrandName}</CardTitle>
                        <Badge variant="outline" className="bg-primary/10">
                          Scraping
                        </Badge>
                      </div>
                      <CardDescription>
                        {scrape.progress.completed} of {scrape.progress.total} sources complete
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="space-y-2">
                          {scrape.sources.map(source => {
                            const status = scrape.scrapingStatus[source]
                            return (
                              <div key={source} className="flex items-center gap-2 text-sm">
                                {status === 'completed' ? (
                                  <Check className="h-4 w-4 text-green-500 flex-shrink-0" />
                                ) : status === 'failed' || status === 'error' ? (
                                  <XCircle className="h-4 w-4 text-red-500 flex-shrink-0" />
                                ) : (
                                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground flex-shrink-0" />
                                )}
                                <span className="capitalize text-muted-foreground">{source.replace(/_/g, ' ')}</span>
                              </div>
                            )
                          })}
                        </div>
                        {scrape.error && (
                          <div className="flex gap-2 items-start text-xs text-destructive bg-destructive/10 p-2 rounded">
                            <AlertCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                            <span>{scrape.error}</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}

                {/* Regular Brand Cards */}
                {filteredBrands.map((brand) => (
                  <Link key={brand.name} href={`/dashboard/${encodeURIComponent(brand.name)}`}>
                    <Card className="hover:border-primary transition-colors cursor-pointer h-full">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-xl">{brand.name}</CardTitle>
                          <Badge variant={brand.status === 'active' ? 'default' : 'secondary'}>
                            {brand.status === 'active' ? 'Active' : 'Inactive'}
                          </Badge>
                        </div>
                        <CardDescription className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          Last updated: {formatDate(brand.lastUpdated)}
                        </CardDescription>
                      </CardHeader>
                      {brand.stats && (
                        <CardContent>
                          <div className="space-y-2">
                            <div className="flex items-center justify-between text-sm">
                              <span className="text-muted-foreground">Total Entries</span>
                              <span className="font-medium">{brand.stats.total_entries || 0}</span>
                            </div>
                            {brand.stats.avg_reputation_score !== undefined && (
                              <div className="flex items-center justify-between text-sm">
                                <span className="text-muted-foreground">Avg. Score</span>
                                <div className="flex items-center gap-1">
                                  <TrendingUp className="h-3 w-3 text-green-500" />
                                  <span className="font-medium">
                                    {(brand.stats.avg_reputation_score * 100).toFixed(1)}%
                                  </span>
                                </div>
                              </div>
                            )}
                            {brand.stats.sources && Object.keys(brand.stats.sources).length > 0 && (
                              <div className="pt-2 border-t border-border">
                                <span className="text-xs text-muted-foreground">
                                  Sources: {Object.keys(brand.stats.sources).join(', ')}
                                </span>
                              </div>
                            )}
                          </div>
                        </CardContent>
                      )}
                    </Card>
                  </Link>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
