import { Hero } from "@/components/Hero";
import { WhyNotRag } from "@/components/WhyNotRag";
import { L1Demo } from "@/components/L1Demo";
import { MultiLDemo } from "@/components/MultiLDemo";
import { Presets } from "@/components/Presets";
import { UnderTheHood } from "@/components/UnderTheHood";
import { GetStarted } from "@/components/GetStarted";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <main className="pt-16">
      <Hero />
      <WhyNotRag />
      <L1Demo />
      <MultiLDemo />
      <Presets />
      <UnderTheHood />
      <GetStarted />
      <Footer />
    </main>
  );
}
