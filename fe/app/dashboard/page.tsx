'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { fetchBrandsWithStats, type Brand, type BrandStats } from '@/lib/api'
import { Search, Plus, TrendingUp, Clock, RefreshCw, AlertCircle } from 'lucide-react'

export const dynamic = 'force-dynamic'

type BrandWithStats = Brand & { stats?: BrandStats }

export default function Dashboard() {
  const [brands, setBrands] = useState<BrandWithStats[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

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

  useEffect(() => {
    loadBrands()
  }, [])

  const filteredBrands = brands.filter(brand =>
    brand.name.toLowerCase().includes(searchQuery.toLowerCase())
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
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Brand
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Brand</DialogTitle>
                <DialogDescription>
                  Add a new brand to track its reputation across different platforms.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <p className="text-sm text-muted-foreground">
                  Feature coming soon...
                </p>
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
            {filteredBrands.length === 0 ? (
              <Card>
                <CardContent className="pt-6">
                  <p className="text-center text-muted-foreground">
                    {searchQuery ? 'No brands found matching your search.' : 'No brands tracked yet. Add one to get started!'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
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
