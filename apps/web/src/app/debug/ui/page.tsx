import * as React from "react"
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Badge,
  Skeleton,
  Callout,
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@sarathi/ui"

export default function DebugUIPage() {
  return (
    <div className="container mx-auto max-w-4xl py-12 space-y-16">
      <div>
        <h1 className="text-3xl font-bold mb-2">UI Primitives Debug</h1>
        <p className="text-muted-foreground">Verification of design tokens and components.</p>
      </div>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Buttons</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <Button variant="default">Default</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="link">Link</Button>
        </div>
        <div className="flex flex-wrap gap-4 items-center">
          <Button size="sm">Small</Button>
          <Button size="default">Default Size</Button>
          <Button size="lg">Large Size</Button>
          <Button size="icon">X</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Badges</h2>
        <div className="flex flex-wrap gap-4">
          <Badge variant="default">Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="outline">Outline</Badge>
        </div>
        <h3 className="text-sm font-medium text-muted-foreground">Mastery Scale</h3>
        <div className="flex flex-wrap gap-4">
          <Badge variant="mastery1">Level 1</Badge>
          <Badge variant="mastery2">Level 2</Badge>
          <Badge variant="mastery3">Level 3</Badge>
          <Badge variant="mastery4">Level 4</Badge>
          <Badge variant="mastery5">Level 5</Badge>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Inputs & Labels</h2>
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <Label htmlFor="email">Email</Label>
          <Input type="email" id="email" placeholder="Email" />
        </div>
        <div className="grid w-full max-w-sm items-center gap-1.5">
          <Label htmlFor="disabled">Disabled</Label>
          <Input disabled type="text" id="disabled" placeholder="Disabled input" />
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Callouts</h2>
        <div className="grid gap-4">
          <Callout variant="info" title="Information">
            This is an informational callout providing extra context.
          </Callout>
          <Callout variant="tip" title="Pro Tip">
            This is a helpful tip to guide the learner.
          </Callout>
          <Callout variant="warning" title="Warning">
            This is a warning about a potential pitfall.
          </Callout>
          <Callout variant="misconception" title="Common Misconception">
            This addresses a common misunderstanding. Notice it's distinct from the warning.
          </Callout>
          <Callout variant="ai_notice" title="AI Generated">
            This content was adapted dynamically by the tutor AI.
          </Callout>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Card</h2>
        <Card className="w-[350px]">
          <CardHeader>
            <CardTitle>Lesson Title</CardTitle>
            <CardDescription>A brief description of this module.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm">Card content goes here. It provides a standard container for grouped information.</p>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline">Cancel</Button>
            <Button>Continue</Button>
          </CardFooter>
        </Card>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Tabs</h2>
        <Tabs defaultValue="account" className="w-[400px]">
          <TabsList>
            <TabsTrigger value="account">Account</TabsTrigger>
            <TabsTrigger value="password">Password</TabsTrigger>
          </TabsList>
          <TabsContent value="account">
            <Card>
              <CardHeader>
                <CardTitle>Account</CardTitle>
                <CardDescription>Make changes to your account here.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="space-y-1">
                  <Label htmlFor="name">Name</Label>
                  <Input id="name" defaultValue="Pedro Duarte" />
                </div>
              </CardContent>
              <CardFooter>
                <Button>Save changes</Button>
              </CardFooter>
            </Card>
          </TabsContent>
          <TabsContent value="password">
            <Card>
              <CardHeader>
                <CardTitle>Password</CardTitle>
                <CardDescription>Change your password here.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="space-y-1">
                  <Label htmlFor="current">Current password</Label>
                  <Input id="current" type="password" />
                </div>
              </CardContent>
              <CardFooter>
                <Button>Save password</Button>
              </CardFooter>
            </Card>
          </TabsContent>
        </Tabs>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Overlays (Dialog & Sheet)</h2>
        <div className="flex gap-4">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">Open Dialog</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Edit profile</DialogTitle>
                <DialogDescription>
                  Make changes to your profile here. Click save when you're done.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="name2" className="text-right">
                    Name
                  </Label>
                  <Input id="name2" defaultValue="Pedro Duarte" className="col-span-3" />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit">Save changes</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline">Open Sheet (Sidebar)</Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Tutor Chat</SheetTitle>
                <SheetDescription>
                  Ask any questions about the current lesson here.
                </SheetDescription>
              </SheetHeader>
              <div className="py-4">
                <Skeleton className="h-[200px] w-full rounded-md" />
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-semibold border-b pb-2">Skeleton Loading</h2>
        <div className="flex items-center space-x-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-[250px]" />
            <Skeleton className="h-4 w-[200px]" />
          </div>
        </div>
      </section>

    </div>
  )
}
