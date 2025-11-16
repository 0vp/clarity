const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export interface Brand {
  name: string;
  last_updated?: string;
  status?: 'active' | 'inactive';
  lastUpdated?: string;
}

export interface BrandStats {
  total_entries: number;
  average_score: number;
  by_source: Record<string, {
    count: number;
    avg_score: number;
  }>;
  latest_date?: string;
  date_range?: {
    earliest: string;
    latest: string;
  };
  sources?: Record<string, number>;
  avg_reputation_score?: number;
  latest_entry?: {
    date: string;
    source_type: string;
    reputation_score: number;
  };
}

export interface BrandData {
  date: string;
  source_url: string;
  source_type: string;
  reputation_score: number;
  summary: string;
  scraped_at: string;
  raw_data?: string;
}

export async function fetchBrands(): Promise<Brand[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/brands`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch brands: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.brands.map((brand: any) => ({
      name: brand.name,
      last_updated: brand.last_updated,
      lastUpdated: brand.last_updated
    }));
  } catch (error) {
    console.error('Error fetching brands:', error);
    throw error;
  }
}

export async function fetchBrandStats(
  brandName: string,
  startDate?: string,
  endDate?: string
): Promise<BrandStats> {
  try {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    
    const url = `${API_BASE_URL}/brands/${encodeURIComponent(brandName)}/stats${params.toString() ? '?' + params.toString() : ''}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch brand stats: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data.stats;
  } catch (error) {
    console.error(`Error fetching stats for ${brandName}:`, error);
    throw error;
  }
}

export async function fetchBrandData(
  brandName: string,
  options?: {
    startDate?: string;
    endDate?: string;
    date?: string;
    limit?: number;
  }
): Promise<BrandData[]> {
  try {
    const params = new URLSearchParams();
    
    if (options?.date) {
      params.append('date', options.date);
    } else {
      if (options?.startDate) params.append('start_date', options.startDate);
      if (options?.endDate) params.append('end_date', options.endDate);
    }
    
    if (options?.limit) params.append('limit', options.limit.toString());
    
    const url = `${API_BASE_URL}/brands/${encodeURIComponent(brandName)}/data?${params}`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch brand data: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.data;
  } catch (error) {
    console.error(`Error fetching data for ${brandName}:`, error);
    throw error;
  }
}

export async function fetchBrandDataRange(
  brandName: string,
  days: number = 30
): Promise<BrandData[]> {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - days);
  
  return fetchBrandData(brandName, {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  });
}

export async function fetchBrandLatestData(
  brandName: string,
  limit: number = 10,
  offset: number = 0
): Promise<BrandData[]> {
  try {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (offset > 0) {
      params.append('offset', offset.toString());
    }
    
    const response = await fetch(
      `${API_BASE_URL}/brands/${encodeURIComponent(brandName)}/latest?${params}`
    );
    
    if (!response.ok) {
      throw new Error(`Failed to fetch latest brand data: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.data;
  } catch (error) {
    console.error(`Error fetching latest data for ${brandName}:`, error);
    throw error;
  }
}

export async function fetchBrandsWithStats(): Promise<Array<Brand & { stats?: BrandStats }>> {
  try {
    const brands = await fetchBrands();
    
    const brandsWithStats = await Promise.all(
      brands.map(async (brand) => {
        try {
          const stats = await fetchBrandStats(brand.name);
          
          // Use last_updated from brands endpoint first, fallback to stats
          const lastUpdated = brand.last_updated || stats.latest_entry?.date || stats.date_range?.latest;
          const isRecent = lastUpdated 
            ? new Date(lastUpdated) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
            : false;
          
          return {
            ...brand,
            stats,
            lastUpdated,
            status: isRecent ? 'active' as const : 'inactive' as const,
          };
        } catch (error) {
          // Even if stats fail, we have last_updated from brands endpoint
          const lastUpdated = brand.last_updated;
          const isRecent = lastUpdated 
            ? new Date(lastUpdated) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
            : false;
          
          return {
            ...brand,
            lastUpdated,
            status: isRecent ? 'active' as const : 'inactive' as const,
          };
        }
      })
    );
    
    return brandsWithStats;
  } catch (error) {
    console.error('Error fetching brands with stats:', error);
    throw error;
  }
}
