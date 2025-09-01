from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Quiz, Question, User, Score
from datetime import datetime
from sqlalchemy.exc import IntegrityError

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('user.dashboard'))

@admin_bp.route('/dashboard')
def dashboard():
    stats = {
        'users': User.query.filter_by(is_admin=False).count(),
        'subjects': Subject.query.count(),
        'quizzes': Quiz.query.count(),
        'attempts': Score.query.count()
    }
    return render_template('admin_dashboard.html', stats=stats)

@admin_bp.route('/subjects')
def manage_subjects():
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('manage_subjects.html', subjects=subjects)

@admin_bp.route('/subject/add', methods=['POST'])
def add_subject():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash('Subject name is required', 'danger')
        return redirect(url_for('admin.manage_subjects'))
    
    try:
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully', 'success')
    except IntegrityError:
        db.session.rollback()
        flash('Subject name already exists', 'danger')
    
    return redirect(url_for('admin.manage_subjects'))

@admin_bp.route('/subject/<int:subject_id>/delete', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin.manage_subjects'))

@admin_bp.route('/chapters/<int:subject_id>')
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    return render_template('manage_chapters.html', subject=subject)

@admin_bp.route('/chapter/add', methods=['POST'])
def add_chapter():
    subject_id = request.form.get('subject_id')
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not all([subject_id, name]):
        flash('Chapter name and subject are required', 'danger')
        return redirect(url_for('admin.manage_chapters', subject_id=subject_id))
    
    chapter = Chapter(
        name=name,
        description=description,
        subject_id=subject_id
    )
    db.session.add(chapter)
    db.session.commit()
    flash('Chapter added successfully', 'success')
    return redirect(url_for('admin.manage_chapters', subject_id=subject_id))

@admin_bp.route('/chapter/<int:chapter_id>/delete', methods=['POST'])
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('admin.manage_chapters', subject_id=subject_id))

@admin_bp.route('/quizzes/<int:chapter_id>')
def manage_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('manage_quizzes.html', chapter=chapter)

@admin_bp.route('/quiz/add', methods=['POST'])
def add_quiz():
    chapter_id = request.form.get('chapter_id')
    duration = request.form.get('duration')
    remarks = request.form.get('remarks', '').strip()
    
    if not all([chapter_id, duration]):
        flash('Duration and chapter are required', 'danger')
        return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))
    
    try:
        quiz = Quiz(
            chapter_id=chapter_id,
            time_duration=int(duration),
            remarks=remarks
        )
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz created successfully', 'success')
    except ValueError:
        db.session.rollback()
        flash('Invalid duration format', 'danger')
    
    return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))

@admin_bp.route('/quiz/<int:quiz_id>/questions')
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    return render_template('manage_questions.html', quiz=quiz)

@admin_bp.route('/question/add', methods=['POST'])
def add_question():
    quiz_id = request.form.get('quiz_id')
    quiz = Quiz.query.get_or_404(quiz_id)
    
    question = Question(
        quiz_id=quiz_id,
        question_statement=request.form.get('statement', '').strip(),
        option1=request.form.get('option1', '').strip(),
        option2=request.form.get('option2', '').strip(),
        option3=request.form.get('option3', '').strip() or None,
        option4=request.form.get('option4', '').strip() or None,
        correct_option=int(request.form.get('correct_option'))
    )
    
    db.session.add(question)
    db.session.commit()
    flash('Question added successfully', 'success')
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

@admin_bp.route('/question/<int:question_id>/delete', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

@admin_bp.route('/users')
def manage_users():
    users = User.query.filter_by(is_admin=False).order_by(User.username).all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    if current_user.id == user_id:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/scores')
def view_scores():
    scores = Score.query.order_by(Score.timestamp.desc()).all()
    return render_template('view_scores.html', scores=scores)