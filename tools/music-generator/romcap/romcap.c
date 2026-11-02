/* romcap: run a GBA ROM headless in libmgba as fast as the CPU allows and record, frame by frame and with no
 * real-time audio device in the way, everything a music-to-picture check needs:
 *   <out>/log.csv    emu_frame, then one column per watched address (u32 reads), one row per frame
 *   <out>/audio.raw  the core's audio, s16 stereo at <out>/audio.rate Hz, every sample the core produced
 *   <out>/video.raw  (optional) 240x160 RGBA frames, one per emulated frame, for ffmpeg -f rawvideo
 *
 *   romcap ROM OUT_DIR FRAMES VIDEO_FROM name=0xADDR [name=0xADDR ...]
 *
 * VIDEO_FROM: first frame to write to video.raw (-1: no video). Built by romsync.py against the mGBA 0.11 that
 * tools/play-tester/scripts/setup-ubuntu.sh installs in /opt/mgba-0.11. The real-time frontends drop or pad
 * audio when the emulator runs slower than real time (they did in this container); this one cannot. */
#include <mgba/flags.h>
#include <mgba/core/core.h>
#include <mgba/core/config.h>
#include <mgba/core/log.h>
#include <mgba-util/audio-buffer.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quiet(struct mLogger* logger, int category, enum mLogLevel level, const char* format, va_list args) {
	(void) logger; (void) category; (void) level; (void) format; (void) args;
}

int main(int argc, char** argv) {
	if (argc < 5) {
		fprintf(stderr, "usage: romcap ROM OUT_DIR FRAMES VIDEO_FROM [name=0xADDR ...]\n");
		return 2;
	}
	const char* rom = argv[1];
	const char* out = argv[2];
	long frames = strtol(argv[3], NULL, 10);
	long videoFrom = strtol(argv[4], NULL, 10);
	int nWatch = argc - 5;
	char** names = calloc(nWatch, sizeof(char*));
	uint32_t* addrs = calloc(nWatch, sizeof(uint32_t));
	for (int i = 0; i < nWatch; ++i) {
		char* eq = strchr(argv[5 + i], '=');
		if (!eq) {
			fprintf(stderr, "bad watch %s\n", argv[5 + i]);
			return 2;
		}
		*eq = '\0';
		names[i] = argv[5 + i];
		addrs[i] = strtoul(eq + 1, NULL, 0);
	}

	static struct mLogger logger = { .log = quiet };
	mLogSetDefaultLogger(&logger);

	struct mCore* core = mCoreFind(rom);
	if (!core || !core->init(core)) {
		fprintf(stderr, "cannot open %s\n", rom);
		return 1;
	}
	mCoreInitConfig(core, "romcap");
	// with no config file the core's master volume defaults to 0: everything would record as silence
	mCoreConfigSetDefaultIntValue(&core->config, "volume", 0x100);
	mCoreConfigSetDefaultIntValue(&core->config, "mute", 0);
	mCoreLoadConfig(core);
	unsigned w, h;
	core->baseVideoSize(core, &w, &h);
	mColor* video = calloc(w * h, sizeof(mColor));
	core->setVideoBuffer(core, video, w);
	core->setAudioBufferSize(core, 4096);
	if (!mCoreLoadFile(core, rom)) {
		fprintf(stderr, "cannot load %s\n", rom);
		return 1;
	}
	core->reset(core);

	char path[4096];
	snprintf(path, sizeof(path), "%s/log.csv", out);
	FILE* log = fopen(path, "w");
	snprintf(path, sizeof(path), "%s/audio.raw", out);
	FILE* aud = fopen(path, "wb");
	FILE* vid = NULL;
	if (videoFrom >= 0) {
		snprintf(path, sizeof(path), "%s/video.raw", out);
		vid = fopen(path, "wb");
	}
	if (!log || !aud) {
		fprintf(stderr, "cannot write to %s\n", out);
		return 1;
	}
	fprintf(log, "emu_frame");
	for (int i = 0; i < nWatch; ++i) {
		fprintf(log, ",%s", names[i]);
	}
	fprintf(log, "\n");

	int16_t samples[2 * 2048];
	struct mAudioBuffer* buf = core->getAudioBuffer(core);
	for (long f = 0; f < frames; ++f) {
		core->runFrame(core);
		size_t n;
		while ((n = mAudioBufferRead(buf, samples, 2048)) > 0) {
			fwrite(samples, sizeof(int16_t) * 2, n, aud);
		}
		fprintf(log, "%ld", f);
		for (int i = 0; i < nWatch; ++i) {
			fprintf(log, ",%u", core->busRead32(core, addrs[i]));
		}
		fprintf(log, "\n");
		if (vid && f >= videoFrom) {
			fwrite(video, sizeof(mColor), w * h, vid);
		}
	}
	snprintf(path, sizeof(path), "%s/audio.rate", out);
	FILE* rate = fopen(path, "w");
	fprintf(rate, "%u\n", core->audioSampleRate(core));
	fclose(rate);
	fclose(log);
	fclose(aud);
	if (vid) {
		fclose(vid);
	}
	core->deinit(core);
	return 0;
}
