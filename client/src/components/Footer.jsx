function Footer() {
  return (
    <footer className="w-full mt-10 py-4 bg-white/70 backdrop-blur-lg border-t text-center text-sm text-gray-600">
      © {new Date().getFullYear()} AI Fact Checker • Built by Shefali & Garima  
      <br />
      <span className="text-gray-400">
        College Project • All rights reserved
      </span>
    </footer>
  );
}

export default Footer;