from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database setup
def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row  # This allows us to access the columns by name
    return conn

# Total movies in database
def count():
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM movies').fetchone()
    conn.close()
    return total

# Home page: View all movies
@app.route('/')
def index():
    conn = get_db_connection()
    total = count()
    movies = conn.execute('SELECT * FROM movies').fetchall()
    conn.close()
    return render_template('index.html', movies=movies, total=total)

# Add a new movie
@app.route('/add', methods=('GET', 'POST'))
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        year = request.form['year']

        conn = get_db_connection()
        total = count()
        conn.execute('INSERT INTO movies (title, genre, year) VALUES (?, ?, ?)', (title, genre, year))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    total = count()
    return render_template('add_movie.html', total=total)

#Search a movie
@app.route('/search', methods=('GET', 'POST'))
def search_movie():
    if request.method == 'POST':
        search_query = request.form['search_query']
        search_by = request.form['search_by']
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Determine the search criteria based on the user's choice
        if search_by == 'title':
            cursor.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + search_query + '%',))
        elif search_by == 'genre':
            cursor.execute("SELECT * FROM movies WHERE genre LIKE ?", ('%' + search_query + '%',))
        elif search_by == 'year':
            cursor.execute("SELECT * FROM movies WHERE year = ?", (search_query,))
        
        movies = cursor.fetchall()
        total = count()
        conn.close()
        
        return render_template('result_search.html', movies=movies , total=total)
    else:
        total = count()
        return render_template('search_movie.html', total=total)     


# Update an existing movie
@app.route('/<int:m_id>/edit', methods=('GET', 'POST'))
def update_movie(m_id):
    conn = get_db_connection()
    movie = conn.execute('SELECT * FROM movies WHERE m_id = ?', (m_id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        genre = request.form['genre']
        year = request.form['year']

        conn.execute('UPDATE movies SET title = ?, genre = ?, year = ? WHERE m_id = ?', (title, genre, year, m_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    total = count()
    conn.close()
    return render_template('update_movie.html', movie=movie, total=total)

# Delete a movie
@app.route('/<int:m_id>/delete', methods=('POST',))
def delete_movie(m_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM movies WHERE m_id = ?', (m_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Sorting by
@app.route('/', methods=('POST',))
def sortby():
    if request.method == 'POST':
        sortby = request.form['sortby']

        conn = get_db_connection()
        cursor = conn.cursor()

        if sortby == 'title':
            cursor.execute("SELECT * FROM movies ORDER BY title")
        elif sortby == 'genre':
            cursor.execute("SELECT * FROM movies ORDER BY genre")
        elif sortby == 'year':
            cursor.execute("SELECT * FROM movies ORDER BY year")
        
        movies = cursor.fetchall()
        total = count()
        conn.commit()
        conn.close()
        
        return render_template('index.html', movies=movies, total=total)


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
    app.run(debug=True)
