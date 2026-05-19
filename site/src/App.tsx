import Hero from "./components/Hero"
import Install from "./components/Install"
import PlaygroundDemo from "./components/PlaygroundDemo"
import HowItWorks from "./components/HowItWorks"
import Footer from "./components/Footer"

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <Hero />
      <Install />
      <PlaygroundDemo />
      <HowItWorks />
      <Footer />
    </div>
  )
}
