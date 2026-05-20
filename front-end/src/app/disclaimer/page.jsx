export default function Disclaimer() {
    return (
        <div className="container py-5">
            <div className="mx-auto" style={{maxWidth: '800px'}}>
                <h1 className="fw-bold mb-2">Aviso Legal (Disclaimer)</h1>
                <p className="text-muted mb-4">Atualizado em Maio de 2026</p>
                
                <div className="card border-0 shadow-sm p-4 p-md-5">
                    <p className="lead fw-bold text-primary">
                        O projeto Conecta Alta Paulista tem finalidade exclusivamente acadêmica, educativa e informativa.
                    </p>
                    <hr className="my-4" />
                    
                    <h5 className="fw-bold"><i className="bi bi-robot text-secondary me-2"></i>Sobre o Conteúdo e Automação</h5>
                    <p className="text-muted">
                        Todas as notícias, resumos e dados veiculados nesta plataforma são coletados de forma 100% automatizada por meio de algoritmos de Web Scraping e feeds RSS. Nossa equipe <strong>não cria, não edita e não altera</strong> o conteúdo original das matérias jornalísticas.
                    </p>
                    
                    <h5 className="fw-bold mt-4"><i className="bi bi-shield-exclamation text-secondary me-2"></i>Isenção de Responsabilidade Editorial</h5>
                    <p className="text-muted">
                        A equipe de desenvolvedores deste sistema atua estritamente na elaboração da arquitetura tecnológica de software. Não possuímos opinião embasada sobre os assuntos abordados. O teor, a veracidade, as imagens e as opiniões expressas nas notícias são de <strong>total e exclusiva responsabilidade dos sites, portais e autores originais</strong> que as publicam.
                    </p>
                    
                    <h5 className="fw-bold mt-4"><i className="bi bi-c-circle text-secondary me-2"></i>Direitos Autorais e Tráfego</h5>
                    <p className="text-muted">
                        O sistema funciona como um indexador digital regional. Ao clicar em "Ver Matéria Completa", o usuário é sempre redirecionado para o site oficial da fonte geradora da notícia, garantindo o tráfego e respeitando integralmente os direitos de propriedade intelectual dos autores originais.
                    </p>
                    
                    <h5 className="fw-bold mt-4"><i className="bi bi-database text-secondary me-2"></i>Uso de Dados</h5>
                    <p className="text-muted">
                        Os dados coletados no cadastro (e-mail, nome e preferências) servem exclusivamente para o funcionamento do sistema de login e personalização de filtros do feed. O projeto não possui viés comercial, não exibe anúncios, não busca monetização e <strong>não comercializa dados com terceiros</strong>.
                    </p>
                </div>
            </div>
        </div>
    );
}