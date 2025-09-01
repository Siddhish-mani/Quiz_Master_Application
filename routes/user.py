from models import Question  # Add this with your other imports
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Quiz, Score  # Make sure all models are imported
from datetime import datetime
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    # Get subjects with quiz counts (with explicit joins)
    subjects = db.session.query(
        Subject,
        func.count(Quiz.id).label('quiz_count')
    ).select_from(Subject
    ).join(Chapter, Subject.id == Chapter.subject_id
    ).join(Quiz, Chapter.id == Quiz.chapter_id
    ).group_by(Subject.id).all()
    
    # Get user's recent scores with explicit joins
    recent_scores = Score.query.filter_by(
        user_id=current_user.id
    ).join(Score.quiz  # Use relationship attribute
    ).join(Quiz.chapter  # Use relationship attribute
    ).join(Chapter.subject  # Use relationship attribute
    ).order_by(
        Score.timestamp.desc()
    ).limit(5).all()
    
    # Calculate overall performance
    total_attempts = Score.query.filter_by(
        user_id=current_user.id
    ).count()
    
    avg_score = db.session.query(
        func.avg(Score.total_scored * 100.0 / Score.total_questions)
    ).filter(
        Score.user_id == current_user.id
    ).scalar()
    
    return render_template('user_dashboard.html',
                         subjects=subjects,
                         recent_scores=recent_scores,
                         total_attempts=total_attempts,
                         avg_score=round(avg_score or 0, 2))

@user_bp.route('/subject/<int:subject_id>')
@login_required
def view_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(
        subject_id=subject_id
    ).options(
        db.joinedload(Chapter.quizzes)
    ).all()
    
    return render_template('view_subject.html',
                         subject=subject,
                         chapters=chapters)

@user_bp.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.options(
        db.joinedload(Quiz.questions)  # Eager load questions
    ).get_or_404(quiz_id)
    
    if request.method == 'POST':
        score = 0
        questions = quiz.questions
        
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                score += 1
        
        # Save the score
        new_score = Score(
            quiz_id=quiz.id,
            user_id=current_user.id,
            total_scored=score,
            total_questions=len(questions)
        )
        db.session.add(new_score)
        db.session.commit()
        
        flash(f'Quiz completed! Your score: {score}/{len(questions)}', 'success')
        return redirect(url_for('user.quiz_result', quiz_id=quiz.id))
    
    return render_template('attempt_quiz.html', 
                         quiz=quiz,
                         questions=quiz.questions)

@user_bp.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(
        quiz_id=quiz_id,
        user_id=current_user.id
    ).order_by(
        Score.timestamp.desc()
    ).first_or_404()
    
    return render_template('quiz_result.html',
                         quiz=quiz,
                         score=score)

@user_bp.route('/scores')
@login_required
def view_my_scores():
    scores = Score.query.filter_by(
        user_id=current_user.id
    ).join(Quiz).join(Chapter).join(Subject).options(
        db.joinedload(Score.quiz).joinedload(Quiz.chapter).joinedload(Chapter.subject)
    ).order_by(Score.timestamp.desc()).all()

    return render_template('view_my_scores.html', scores=scores)  # Let the model handle percentage!