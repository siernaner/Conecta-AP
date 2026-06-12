import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { AuthProvider } from '../contexts/AuthContext';
import NavBar from './NavBar';
import Link from 'next/link';

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="bg-light d-flex flex-column min-vh-100" style={{ paddingTop: '56px' }}>
        <AuthProvider>
           <NavBar />
           <main className="container py-4 flex-grow-1">
              {children}
           </main>
           <footer className="bg-dark text-light py-4 mt-auto">
                <div className="container text-center">
                    <div className="d-flex justify-content-center gap-4 mb-3">
                        <Link href="/sobre" className="text-light text-decoration-none" style={{ fontSize: '1rem' }}>Sobre o Projeto</Link>
                        <Link href="/disclaimer" className="text-light text-decoration-none" style={{ fontSize: '1rem' }}>Aviso Legal</Link>
                        <Link href="/contato" className="text-light text-decoration-none" style={{ fontSize: '1rem' }}>Contato</Link>
                    </div>
                    <p className="mb-1 text-muted" style={{ fontSize: '0.9rem' }}>
                        Este sistema possui fins estritamente educativos e acadêmicos, sem fins lucrativos.
                    </p>
                    <p className="mb-0 text-muted" style={{ fontSize: '0.8rem' }}>
                        As notícias têm origens externas e são de responsabilidade dos autores originais.
                    </p>
                </div>
           </footer>
        </AuthProvider>
      </body>
    </html>
  );
}