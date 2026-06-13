import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { PageHeader } from '@/components/layout/PageHeader'
import { getInitials } from '@/lib/utils'
import api from '@/lib/api'

export default function ProfilePage() {
  const { user, refreshUser } = useAuth()
  const [firstName, setFirstName] = useState(user?.first_name || '')
  const [lastName, setLastName] = useState(user?.last_name || '')
  const [phone, setPhone] = useState(user?.phone || '')
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')

  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [changingPassword, setChangingPassword] = useState(false)
  const [passwordMessage, setPasswordMessage] = useState('')

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSaving(true)
    setMessage('')
    try {
      await api.patch('/auth/profile/', { first_name: firstName, last_name: lastName, phone })
      await refreshUser()
      setMessage('Profile updated successfully')
    } catch {
      setMessage('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    setChangingPassword(true)
    setPasswordMessage('')
    try {
      await api.put('/auth/change-password/', { old_password: oldPassword, new_password: newPassword })
      setPasswordMessage('Password changed successfully')
      setOldPassword('')
      setNewPassword('')
    } catch {
      setPasswordMessage('Failed to change password')
    } finally {
      setChangingPassword(false)
    }
  }

  return (
    <div>
      <PageHeader title="Profile" description="Manage your account settings" />

      <div className="grid gap-6 md:grid-cols-3">
        {/* Profile Card */}
        <Card>
          <CardContent className="flex flex-col items-center p-6">
            <Avatar className="h-24 w-24">
              <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                {user ? getInitials(user.full_name) : '?'}
              </AvatarFallback>
            </Avatar>
            <h3 className="mt-4 text-lg font-semibold">{user?.full_name}</h3>
            <p className="text-sm text-muted-foreground">{user?.email}</p>
            <p className="mt-1 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium capitalize text-primary">
              {user?.role?.replace('_', ' ')}
            </p>
            <Separator className="my-4" />
            <div className="w-full space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Phone</span>
                <span>{user?.phone || 'Not set'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Joined</span>
                <span>{user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : ''}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">MFA</span>
                <span>{user?.mfa_enabled ? 'Enabled' : 'Disabled'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Edit Profile */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Edit Profile</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              {message && (
                <div className="rounded-md bg-primary/10 px-4 py-2 text-sm text-primary">{message}</div>
              )}
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>First Name</Label>
                  <Input value={firstName} onChange={(e) => setFirstName(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label>Last Name</Label>
                  <Input value={lastName} onChange={(e) => setLastName(e.target.value)} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Phone</Label>
                <Input value={phone} onChange={(e) => setPhone(e.target.value)} />
              </div>
              <Button type="submit" disabled={saving}>
                {saving ? 'Saving...' : 'Save Changes'}
              </Button>
            </form>

            <Separator className="my-6" />

            <h3 className="mb-4 text-lg font-semibold">Change Password</h3>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              {passwordMessage && (
                <div className="rounded-md bg-primary/10 px-4 py-2 text-sm text-primary">{passwordMessage}</div>
              )}
              <div className="space-y-2">
                <Label>Current Password</Label>
                <Input type="password" value={oldPassword} onChange={(e) => setOldPassword(e.target.value)} required />
              </div>
              <div className="space-y-2">
                <Label>New Password</Label>
                <Input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required />
              </div>
              <Button type="submit" variant="outline" disabled={changingPassword}>
                {changingPassword ? 'Changing...' : 'Change Password'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
