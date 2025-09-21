from django import forms

class ReplyForm(forms.Form):
    """
    Простая форма для ответа пользователю.
    """
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'form-control',
            'placeholder': 'Введите ваш ответ пользователю...'
        }),
        label='Ответ'
    )
