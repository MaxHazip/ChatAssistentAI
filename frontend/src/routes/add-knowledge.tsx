// frontend/src/routes/add-knowledge.tsx
import { useState, type FormEvent, type ChangeEvent } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

export const Route = createFileRoute('/add-knowledge')({
  component: AddKnowledgePage,
})

function AddKnowledgePage() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    
    if (!question.trim() || !answer.trim()) {
      setMessage({ type: 'error', text: 'Заполните оба поля' })
      return
    }

    setIsLoading(true)
    setMessage(null)
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/v1/knowledge/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question.trim(),
          answer: answer.trim(),
          metadata: { source: 'manual_form' }
        }),
      })

      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка сервера')
      }
      
      setMessage({ type: 'success', text: data.message || 'Запись успешно добавлена' })
      setQuestion('')
      setAnswer('')
      
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || 'Не удалось добавить запись' })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="container max-w-3xl mx-auto py-8 px-4">
        <Card className="border-gray-200 shadow-sm bg-white">
          <CardHeader className="space-y-1 pb-4">
            <CardTitle className="text-xl font-semibold text-gray-900">
              Добавить в базу знаний
            </CardTitle>
            <CardDescription className="text-gray-500">
              Введите вопрос и соответствующий ответ. Данные будут сохранены в векторной базе для использования в чате.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="question" className="text-sm font-medium text-gray-700">
                  Вопрос
                </Label>
                <Input
                  id="question"
                  placeholder="Введите вопрос..."
                  value={question}
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setQuestion(e.target.value)}
                  disabled={isLoading}
                  className="h-10 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="answer" className="text-sm font-medium text-gray-700">
                  Ответ
                </Label>
                <textarea
                  id="answer"
                  placeholder="Введите ответ..."
                  value={answer}
                  onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setAnswer(e.target.value)}
                  disabled={isLoading}
                  rows={5}
                  className="flex min-h-[100px] w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                />
              </div>
              
              {message && (
                <div
                  className={`rounded-md border px-4 py-3 text-sm ${
                    message.type === 'success'
                      ? 'border-green-300 bg-green-50 text-green-700'
                      : 'border-red-300 bg-red-50 text-red-700'
                  }`}
                >
                  {message.text}
                </div>
              )}
              
              <div className="flex items-center gap-3 pt-2">
                <Button 
                  type="submit" 
                  disabled={isLoading} 
                  className="min-w-[140px] bg-blue-600 hover:bg-blue-700 text-white"
                >
                  {isLoading ? 'Сохранение...' : 'Сохранить'}
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  onClick={() => {
                    setQuestion('')
                    setAnswer('')
                    setMessage(null)
                  }}
                  disabled={isLoading}
                  className="text-gray-500 hover:text-gray-700 hover:bg-gray-100"
                >
                  Очистить
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}