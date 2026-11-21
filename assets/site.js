// Hero video: a pause/play button (moving content needs one), and no autoplay for people who asked for less motion.
const video = document.querySelector(".screen video");
const toggle = document.querySelector(".video-toggle");
if (video && toggle) {
  const show = () => {
    toggle.classList.toggle("is-paused", video.paused);
    toggle.setAttribute("aria-label", video.paused ? toggle.dataset.play : toggle.dataset.pause);
  };
  toggle.addEventListener("click", () => (video.paused ? video.play() : video.pause()));
  video.addEventListener("play", show);
  video.addEventListener("pause", show);
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) video.pause();
  show();
}

// Language menu: go to the same page in the chosen language.
document.querySelector(".lang select")?.addEventListener("change", (e) => {
  location.href = e.target.value;
});
