import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Rotas que requerem autenticação
const protectedRoutes = ['/dashboard', '/etl', '/data-quality', '/metrics', '/alerts', '/history', '/profile']

// Rotas públicas (não redirecionar se já autenticado)
const publicRoutes = ['/login', '/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // Verificar se é uma rota protegida
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname.startsWith(route)
  )
  
  // Verificar se é uma rota pública
  const isPublicRoute = publicRoutes.some(route => 
    pathname === route || pathname.startsWith(route)
  )
  
  // Para desenvolvimento, permitir todas as rotas
  // Em produção, implementar verificação de autenticação
  if (process.env.NODE_ENV === 'development') {
    return NextResponse.next()
  }
  
  // Em produção, verificar autenticação
  if (isProtectedRoute) {
    // Verificar token de autenticação Supabase
    const token = request.cookies.get('sb-access-token')?.value
    if (!token) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }
  
  // Se acessando rotas públicas com token, redirecionar para dashboard
  if (isPublicRoute) {
    const token = request.cookies.get('sb-access-token')?.value
    if (token) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
  }
  
  // Adicionar headers de segurança
  const response = NextResponse.next()
  
  response.headers.set('X-Frame-Options', 'DENY')
  response.headers.set('X-Content-Type-Options', 'nosniff')
  response.headers.set('Referrer-Policy', 'origin-when-cross-origin')
  response.headers.set('X-XSS-Protection', '1; mode=block')
  
  return response
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
