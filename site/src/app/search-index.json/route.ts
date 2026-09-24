import { getSearchIndex } from '@/lib/content'

/**
 * The search index as one static file, rendered at build time.
 *
 * It used to be passed to the search dialog as props from the root layout, which
 * embedded it in every page's HTML. With the case studies and their tutorials it grew
 * past a megabyte, so it is now fetched once, the first time a reader opens search,
 * and cached by the browser and CDN like any other static asset.
 */
export const dynamic = 'force-static'

export async function GET() {
  return Response.json(await getSearchIndex())
}
