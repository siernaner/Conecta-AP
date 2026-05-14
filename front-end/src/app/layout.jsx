import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import { AuthProvider } from '../contexts/AuthContext';
import NavBar from './NavBar';

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="bg-light d-flex flex-column min-vh-100">
        <AuthProvider>
           <NavBar />
           <main className="container py-4 flex-grow-1">
              {children}
           </main>
           <footer className="bg-dark text-light py-3 mt-auto">
                <div className="container text-center">
                    <p className="small mb-1" style={{ fontSize: '1em' }}>
                        Este sistema foi desenvolvido como uma ferramenta prática e possui <strong>fins estritamente educativos e acadêmicos</strong>, não buscando qualquer tipo de lucro, monetização ou viés comercial.

Todas as notícias e resumos veiculados no site têm origens externas e são extraídos de forma automatizada (via RSS e Web Scraping) de portais de notícias regionais e sites oficiais de prefeituras. 

A equipe de desenvolvedores do sistema atua estritamente na elaboração da arquitetura tecnológica. <strong>Os alunos desenvolvedores não possuem opinião embasada sobre os assuntos abordados nas matérias</strong>. O teor, a veracidade e as opiniões expressas nas notícias são de <strong>total e exclusiva responsabilidade dos sites e autores originais</strong> que as publicam.
                    </p>
                    <p className="small mb-2 text-muted" style={{ fontSize: '0.7rem' }}>
                        As notícias têm origens externas e são de responsabilidade dos autores originais. Desenvolvedores não possuem opinião sobre os fatos.
                    </p>
                    <div className="border-top border-secondary pt-2">
                        <p className="small mb-0">
                            Criado por <a href="https://github.com/siernaner/" target="_blank" rel="noopener noreferrer" className="text-info text-decoration-none fw-bold">@siernaner</a>
                        </p>
                    </div>
                </div>
           </footer>
        </AuthProvider>
      </body>
    </html>
  );
}