from app import app

# depois adicionar migrations para gerenciar as alterações no banco de dados

if __name__ == '__main__':
	app.run(debug=True)