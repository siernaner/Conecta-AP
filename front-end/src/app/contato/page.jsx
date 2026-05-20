export default function Contato() {
    return (
        <div className="container py-5">
            <div className="mx-auto text-center" style={{maxWidth: '600px'}}>
                <h1 className="fw-bold mb-4">Contato</h1>
                
                <div className="card border-0 shadow-sm p-5 bg-white d-flex flex-column align-items-center">
                    <div className="bg-success-subtle p-4 rounded-circle mb-4" style={{width: 'fit-content'}}>
                        <i className="bi bi-whatsapp text-success" style={{fontSize: '4rem'}}></i>
                    </div>
                    
                    <h3 className="fw-bold mb-3">Fale Conosco</h3>
                    <p className="text-muted mb-4">
                        Dúvidas, sugestões ou suporte técnico? Entre em contato diretamente pelo nosso canal oficial no WhatsApp.
                    </p>

                    <div className="border rounded-pill p-3 px-5 bg-light mb-4">
                        <span className="text-muted d-block small text-uppercase fw-bold mb-1">WhatsApp</span>
                        <h4 className="fw-bold m-0 text-dark">(18) 99722-9958</h4>
                    </div>

                    <a 
                        href="https://wa.me/5518997229958" 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="btn btn-success btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm"
                    >
                        <i className="bi bi-chat-fill me-2"></i> Iniciar Conversa
                    </a>
                    
                    <p className="mt-4 small text-muted">
                        Atendimento em horário comercial.
                    </p>
                </div>
            </div>
        </div>
    );
}