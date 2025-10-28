import tkinter as tk
from tkinter import ttk, messagebox
# Imports corrigidos para usar a estrutura de pacotes
import app.scripts.repository as repository
import app.database.db as db
import app.scripts.validators as validators
import os # Importar os para verificar o remember_me

# Inicializa a base de dados e garante as tabelas mínimas
# Isso agora cria o DB em app/database/servtech.db
db.init_db()

# ----------------------------------
# Tela de Login
# ----------------------------------
class LoginFrame(ttk.Frame):
    def __init__(self, master, on_login_ok):
        """
        Tela de login: recebe usuário e senha e chama o callback quando
        a navegação para a próxima tela deve ocorrer.
        """
        super().__init__(master, padding=12)
        self.on_login_ok = on_login_ok

        ttk.Label(self, text="ServTech - Login", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,12))

        ttk.Label(self, text="Usuário:").grid(row=1, column=0, sticky="e")
        self.ent_user = ttk.Entry(self, width=30)
        self.ent_user.grid(row=1, column=1, sticky="we", pady=4)

        ttk.Label(self, text="Senha:").grid(row=2, column=0, sticky="e")
        self.ent_pass = ttk.Entry(self, width=30, show="*")
        self.ent_pass.grid(row=2, column=1, sticky="we", pady=4)

        # Opção de lembrar credenciais em arquivo local (protótipo)
        self.var_remember = tk.BooleanVar(value=True)
        ttk.Checkbutton(self, text="Lembrar login", variable=self.var_remember).grid(row=3, column=1, sticky="w", pady=(0,8))

        ttk.Button(self, text="Entrar", command=self._do_login).grid(row=4, column=0, columnspan=2, pady=6, sticky="we")

        # Bind "Enter" key to login
        self.ent_user.bind("<Return>", lambda event: self._do_login())
        self.ent_pass.bind("<Return>", lambda event: self._do_login())

        for i in range(2):
            self.columnconfigure(i, weight=1)

        self._check_remember_me() # Tenta preencher campos

    def _check_remember_me(self):
        """Verifica se há credenciais salvas e preenche os campos."""
        if os.path.exists(repository.REMEMBER_FILE):
            try:
                with open(repository.REMEMBER_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content and ";" in content:
                        user, pw = content.split(";", 1)
                        self.ent_user.insert(0, user)
                        self.ent_pass.insert(0, pw)
                        self.var_remember.set(True)
            except IOError as e:
                print(f"Erro ao ler remember_me: {e}")
            except (ValueError, IndexError):
                print("Formato inválido do arquivo remember_me.")


    def _do_login(self):
        """
        Obtém usuário e senha informados, e decide a navegação para a
        próxima tela.
        """
        user = self.ent_user.get()
        pw   = self.ent_pass.get()

        # Validação: Exige preenchimento
        if user.strip() == "" or pw.strip() == "":
            messagebox.showwarning("Login", "Usuário e senha são obrigatórios.")
            return

        # Autenticação simples via repositório
        ok = repository.check_login(user, pw)
        if ok:
            if self.var_remember.get():
                repository.save_remember_me(user, pw)
            else:
                # Se desmarcou, remove o arquivo
                if os.path.exists(repository.REMEMBER_FILE):
                    try:
                        os.remove(repository.REMEMBER_FILE)
                    except OSError as e:
                        print(f"Erro ao remover remember_me: {e}")
            self.on_login_ok(user)
        else:
            messagebox.showerror("Login inválido", "Usuário ou senha incorretos.")

# ----------------------------------
# Tela de Ordens de Serviço
# ----------------------------------
class OrdersFrame(ttk.Frame):
    def __init__(self, master, user):
        """
        Tela principal: cadastro, remoção, busca e listagem das ordens
        de serviço. Mostra o usuário atual no cabeçalho.
        """
        super().__init__(master, padding=12)
        self.user = user
        self.selected_id = None # Para rastrear o ID para atualização

        ttk.Label(self, text=f"ServTech - Ordens de Serviço (usuário: {user})", font=("Arial", 14, "bold")).pack(anchor="w")

        # Formulário de entrada de dados
        form = ttk.LabelFrame(self, text="Dados da Ordem", padding=10) # Usando LabelFrame
        form.pack(fill="x", pady=10)

        ttk.Label(form, text="Cliente:").grid(row=0, column=0, sticky="e")
        self.ent_cliente = ttk.Entry(form, width=30)
        self.ent_cliente.grid(row=0, column=1, sticky="we", padx=4, pady=2)

        ttk.Label(form, text="Descrição:").grid(row=1, column=0, sticky="e")
        self.ent_desc = ttk.Entry(form, width=50)
        self.ent_desc.grid(row=1, column=1, sticky="we", padx=4, pady=2)

        ttk.Label(form, text="Preço (R$):").grid(row=2, column=0, sticky="e")
        self.ent_preco = ttk.Entry(form, width=12)
        self.ent_preco.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(form, text="Status:").grid(row=3, column=0, sticky="e")
        self.cmb_status = ttk.Combobox(form, values=["Aberto","Em andamento","Concluído","Cancelado"], state="readonly")
        self.cmb_status.current(0)
        self.cmb_status.grid(row=3, column=1, sticky="w", padx=4, pady=2)

        # Configura a coluna 1 do form para expandir
        form.columnconfigure(1, weight=1)

        # Ações principais
        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=(6,10))
        ttk.Button(btns, text="Criar / Atualizar", command=self._save).pack(side="left")
        ttk.Button(btns, text="Remover", command=self._delete).pack(side="left", padx=6)
        ttk.Button(btns, text="Limpar Campos", command=self._clear_form).pack(side="left", padx=6) # Botão novo

        # Frame de busca separado à direita
        search_frame = ttk.Frame(btns)
        search_frame.pack(side="right")
        ttk.Button(search_frame, text="Buscar Cliente", command=self._search).pack(side="left")
        ttk.Button(search_frame, text="Recarregar Todos", command=self._reload).pack(side="left", padx=6)


        # Tabela para exibir registros
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=("id","cliente","desc","preco","status"), show="headings", height=10)
        for col, title, w in [("id","ID",60), ("cliente","Cliente",160), ("desc","Descrição",220), ("preco","Preço",90), ("status","Status",120)]:
            self.tree.heading(col, text=title)
            self.tree.column(col, width=w, anchor="w", stretch=True if col in ('cliente', 'desc') else False)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Carrega os dados ao iniciar
        self._reload()

    def _clear_form(self):
        """Limpa os campos do formulário e deseleciona a treeview."""
        self.ent_cliente.delete(0, tk.END)
        self.ent_desc.delete(0, tk.END)
        self.ent_preco.delete(0, tk.END)
        self.cmb_status.current(0)
        self.selected_id = None # Limpa o ID selecionado

        # Deseleciona qualquer item na treeview
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(selection)

    def _on_select(self, _evt):
        """Copia os dados da linha selecionada para o formulário."""
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        values = item["values"]

        self.selected_id = values[0] # Guarda o ID para possível UPDATE

        self.ent_cliente.delete(0, tk.END); self.ent_cliente.insert(0, values[1])
        self.ent_desc.delete(0, tk.END); self.ent_desc.insert(0, values[2])
        self.ent_preco.delete(0, tk.END); self.ent_preco.insert(0, values[3])
        self.cmb_status.set(values[4])

    def _save(self):
        """Lê campos do formulário e solicita a gravação ao repositório."""
        cliente = self.ent_cliente.get()
        desc    = self.ent_desc.get()
        preco   = self.ent_preco.get()
        status  = self.cmb_status.get()

        # Validação usando o validador
        if not validators.is_valid_cliente(cliente):
            messagebox.showwarning("Validação", "O campo Cliente é obrigatório.")
            return

        if not validators.is_valid_preco(preco):
            messagebox.showwarning("Validação", "O campo Preço deve ser um número válido (ex: 100.50 ou 100,50) ou estar vazio.")
            return

        # TODO: A lógica de "Criar / Atualizar" deveria checar self.selected_id
        # para fazer UPDATE em vez de INSERT.
        # A função repository.upsert_order atual só faz INSERT.
        if self.selected_id:
             # Lógica de ATUALIZAÇÃO (UPDATE) - Precisaria de uma nova função no repository
             # Ex: repository.update_order(self.selected_id, cliente, desc, preco, status)
             print(f"Lógica de ATUALIZAR (ID: {self.selected_id}) ainda não implementada.")
             # Por enquanto, vamos apenas inserir como novo
             repository.upsert_order(cliente, desc, preco, status)
        else:
            # Lógica de CRIAÇÃO (INSERT)
            repository.upsert_order(cliente, desc, preco, status)

        self._reload()
        self._clear_form() # Limpa o form após salvar

    def _delete(self):
        """Remove o registro selecionado na tabela, se houver seleção."""
        if not self.selected_id:
            messagebox.showwarning("Remoção", "Selecione uma ordem para remover.")
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover a ordem selecionada?"):
            return

        repository.delete_order(self.selected_id)
        self._reload()
        self._clear_form() # Limpa o form após remover

    def _search(self):
        """Busca registros pelo conteúdo do campo 'Cliente' e exibe na tabela."""
        termo = self.ent_cliente.get()
        if not termo.strip():
            messagebox.showwarning("Busca", "Digite um termo no campo Cliente para buscar.")
            return
        rows = repository.search_orders(termo)
        self._fill(rows)
        self._clear_form() # Limpa o form após a busca

    def _reload(self):
        """Recarrega todos os registros e popula a tabela."""
        rows = repository.list_orders()
        self._fill(rows)
        self._clear_form() # Limpa o form

    def _fill(self, rows):
        """Limpa a tabela e insere as linhas informadas."""
        self.tree.delete(*self.tree.get_children())
        for r in rows:
            self.tree.insert("", "end", values=r)

# ----------------------------------
# Aplicação principal
# ----------------------------------
class App(tk.Tk):
    def __init__(self):
        """Janela raiz: controla a exibição das telas do sistema."""
        super().__init__()
        self.title("ServTech Soluções - Protótipo")
        self.geometry("800x520")
        self.minsize(700, 450) # Tamanho mínimo

        # Configura um estilo
        style = ttk.Style(self)
        try:
            # Tenta usar um tema mais moderno se disponível
            style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        except tk.TclError:
             print("Tema 'clam' não disponível, usando default.")

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self._show_login()

    def _show_login(self):
        """Exibe a tela de login no container principal."""
        for w in self.container.winfo_children():
            w.destroy()
        # Centraliza o LoginFrame
        login_frame_wrapper = ttk.Frame(self.container)
        login_frame_wrapper.pack(fill="both", expand=True, padx=20, pady=20)
        LoginFrame(login_frame_wrapper, on_login_ok=self._on_login_ok).pack(anchor="center")


    def _on_login_ok(self, user):
        """Exibe a tela de ordens quando o login é concluído."""
        for w in self.container.winfo_children():
            w.destroy()
        OrdersFrame(self.container, user=user).pack(fill="both", expand=True)

if __name__ == "__main__":
    App().mainloop()
