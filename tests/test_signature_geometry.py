"""Observable ink behavior, without FFmpeg or a font-name lookup table."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image, ImageDraw

SCRIPTS = Path(__file__).resolve().parents[1]/'skills/dynamic-art-signature/scripts'
sys.path.insert(0, str(SCRIPTS))
from ink_geometry import ink_progress, reveal_times, stroke_profile, fragment_defaults
from render_ink_signature import InkAnimation
from signature_palettes import PALETTES


class SignatureGeometryTests(unittest.TestCase):
    def test_returning_tail_follows_ink_past_right_turn(self):
        im = Image.new('L', (96, 80))
        ImageDraw.Draw(im).line([(15, 15), (75, 15), (75, 60), (15, 60)], 255, 5)
        mask = np.asarray(im)>0
        progress, report = ink_progress(mask, start_point=[15, 15])
        self.assertLess(progress[15, 75], progress[60, 75])
        self.assertLess(progress[60, 75], progress[60, 15])
        self.assertTrue(np.isinf(progress[35, 35]))
        self.assertEqual(report['coverage'], 1.)

    def test_disconnected_accents_do_not_draw_a_connector(self):
        im = Image.new('L', (80, 64))
        draw = ImageDraw.Draw(im)
        draw.line((8, 12, 35, 12), 255, 3)
        draw.line((48, 28, 70, 28), 255, 3)
        mask = np.asarray(im)>0
        times, _, report = reveal_times(mask, .3, .44)
        self.assertEqual(report['components'], 2)
        self.assertTrue(np.isfinite(times[mask]).all())
        self.assertTrue(np.isinf(times[~mask]).all())
        self.assertAlmostEqual(times[mask].max()+report['front_duration'], .44)
        self.assertTrue((times[mask]<.37).any() and (times[mask]>.37).any())

    def test_thin_and_thick_ink_receive_different_parameters(self):
        profiles = []
        for width in [3, 15]:
            im = Image.new('L', (120, 64))
            ImageDraw.Draw(im).line((10, 30, 110, 30), 255, width)
            profiles.append(stroke_profile(np.asarray(im)>0))
        self.assertLess(profiles[0]['median_width_px'], profiles[1]['median_width_px'])
        timing = {'first_start':1.46, 'first_end':1.64}
        thin, thick = [fragment_defaults(p, 960, timing) for p in profiles]
        self.assertGreater(thin['cell_width'], thick['cell_width'])
        self.assertLess(thin['drift'], thick['drift'])
        self.assertLess(thin['rotation'], thick['rotation'])

    def fixture(self, root, effect='ink-fragments', rgba=False):
        bg = (235, 240, 245)
        art = Image.new('RGBA' if rgba else 'RGB', (128, 96),
                        (0, 0, 0, 0) if rgba else bg)
        masks = {}
        lines = {'upper':[(8, 12), (50, 8), (115, 16)],
                 'first':[(14, 36), (14, 68), (42, 48)],
                 'rest':[(55, 38), (65, 67), (85, 48)],
                 'tail':[(85, 73), (115, 73), (115, 85), (80, 85)]}
        colors = {'upper':(10, 20, 30), 'first':(15, 25, 35),
                  'rest':(30, 70, 120), 'tail':(210, 110, 40)}
        draw = ImageDraw.Draw(art)
        for name, points in lines.items():
            mask = Image.new('L', art.size)
            ImageDraw.Draw(mask).line(points, 255, 3)
            mask.save(root/(name+'.png'))
            masks[name] = name+'.png'
            color = colors[name]+(255,) if rgba else colors[name]
            draw.line(points, color, 3)
        art.save(root/'art.png')
        cfg = {'art':'art.png', 'masks':masks, 'background':bg, 'effect':effect}
        config = root/'config.json'
        config.write_text(json.dumps(cfg))
        return config, art, bg

    def test_dark_ink_and_alpha_keep_final_pixels_and_clean_pause(self):
        for alpha in [False, True]:
            with self.subTest(alpha=alpha), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                config, art, bg = self.fixture(root, rgba=alpha)
                a = InkAnimation(config)
                self.assertEqual(a.upper_report['start_source'], 'automatic ink endpoints')
                self.assertEqual(a.tail_report['start_source'], 'nearest body join')
                if alpha:
                    art = Image.alpha_composite(Image.new('RGBA', art.size, (*bg,255)), art).convert('RGB')
                self.assertTrue(np.array_equal(np.asarray(a.frame_at(3.2)), np.asarray(art)))
                pause = np.asarray(a.frame_at(.8))
                self.assertTrue(np.all(pause[~a.masks['upper']]==bg))
                self.assertGreater(len(a.fragments), 0)

    def test_plain_write_does_not_add_particles(self):
        with tempfile.TemporaryDirectory() as temp:
            config, _, _ = self.fixture(Path(temp), effect='write')
            a = InkAnimation(config)
            self.assertEqual(len(a.fragments), 0)
            self.assertFalse(a.masks['rest'].any())
            self.assertTrue(np.isfinite(a.first_times[a.masks['first']]).all())

    def test_word_only_signature_writes_without_an_upper_gesture(self):
        for include_tail in (False, True):
            with self.subTest(tail=include_tail), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                body = Image.new('L', (128, 96))
                draw = ImageDraw.Draw(body)
                draw.line([(12, 60), (32, 32), (42, 65), (82, 48)], 255, 3)
                draw.ellipse((54, 24, 58, 28), fill=255)
                body.save(root / 'first.png')
                masks = {'first': 'first.png'}
                art = Image.composite(Image.new('RGB', body.size, 'white'),
                                      Image.new('RGB', body.size, 'black'), body)
                if include_tail:
                    tail = Image.new('L', body.size)
                    ImageDraw.Draw(tail).line([(83, 48), (104, 52), (120, 40)], 255)
                    tail.save(root / 'tail.png')
                    art.paste('white', mask=tail)
                    masks['tail'] = 'tail.png'
                art.save(root / 'art.png')
                config = root / 'config.json'
                config.write_text(json.dumps({
                    'art': 'art.png', 'masks': masks, 'background': [0, 0, 0],
                }))

                animation = InkAnimation(config)
                self.assertEqual(animation.upper_report['method'], 'empty layer')
                self.assertIsNone(animation.frame_at(.29).getbbox())
                self.assertIsNotNone(animation.frame_at(.7).getbbox())
                self.assertEqual(animation.frame_at(3).tobytes(), art.tobytes())

    def palette_config(self, root):
        art = Image.new('RGBA', (96, 64), (255, 255, 255, 0))
        ImageDraw.Draw(art).rectangle((20, 16, 75, 47), fill='white')
        art.putpixel((75, 32), (255, 255, 255, 128))
        art.putpixel((44, 32), (255, 255, 255, 0))
        art.save(root / 'art.png')
        mask = Image.new('L', art.size)
        ImageDraw.Draw(mask).rectangle((20, 16, 75, 47), fill=255)
        mask.save(root / 'first.png')
        return {'art': 'art.png', 'masks': {'first': 'first.png'}, 'background': [0, 0, 0]}

    def test_gradient_preserves_transparency_and_writing_timing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'config.json'
            original = self.palette_config(root)
            config.write_text(json.dumps(original))
            legacy = InkAnimation(config)
            self.assertEqual(legacy.frame_at(3).getpixel((75, 32)), (128, 128, 128))
            self.assertNotIn('palette', legacy.report())

            config.write_text(json.dumps({**original, 'palette': 'sea-salt-soda'}))
            animation = InkAnimation(config)
            art = animation.frame_at(3)
            self.assertEqual(animation.report()['palette'], 'sea-salt-soda')
            self.assertEqual(animation.t, legacy.t)
            np.testing.assert_array_equal(animation.first_times, legacy.first_times)
            self.assertEqual(art.getpixel((20, 32)), (106, 211, 238))
            self.assertEqual(art.getpixel((47, 32)), (160, 228, 188))
            self.assertEqual(art.getpixel((75, 31)), (217, 246, 137))
            self.assertEqual(art.getpixel((75, 32)), (118, 145, 95))
            self.assertEqual(art.getpixel((44, 32)), animation.bg)
            self.assertEqual(art.getpixel((19, 32)), animation.bg)
            self.assertEqual(animation.frame_at(0).getpixel((20, 32)), animation.bg)

    def test_banded_palettes_blend_at_horizontal_and_diagonal_boundaries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'config.json'
            original = self.palette_config(root)
            config.write_text(json.dumps({**original, 'palette': 'google-color'}))
            art = InkAnimation(config).frame_at(3)
            colors = [(91, 148, 255), (255, 108, 99), (251, 209, 82), (91, 148, 255), (105, 201, 138)]
            for row in (16, 47):
                self.assertEqual([art.getpixel((x, row)) for x in (25, 36, 47, 58, 69)], colors)
                self.assertEqual(art.getpixel((31, row)), (173, 128, 177))
                stripe = np.asarray(art, dtype=np.int16)[row, 20:76]
                self.assertLess(np.abs(np.diff(stripe, axis=0)).max(), 45)

            config.write_text(json.dumps({**original, 'palette': 'hello-split'}))
            art = InkAnimation(config).frame_at(3)
            self.assertEqual(art.getpixel((20, 16)), (255, 120, 151))
            self.assertEqual(art.getpixel((75, 47)), (186, 164, 255))
            self.assertEqual(art.getpixel((32, 16)), art.getpixel((30, 24)))
            self.assertLess(120, art.getpixel((32, 16))[1])
            self.assertLess(art.getpixel((32, 16))[1], art.getpixel((32, 47))[1])
            self.assertLess(art.getpixel((32, 47))[1], 197)

    def test_rgba_palette_recolors_ink_that_matches_source_background(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'config.json'
            original = self.palette_config(root)
            with Image.open(root / 'art.png') as source:
                black_ink = Image.new('RGBA', source.size)
                black_ink.putalpha(source.getchannel('A'))
            black_ink.save(root / 'art.png')
            config.write_text(json.dumps({**original, 'palette': 'cola-red'}))

            animation = InkAnimation(config)
            art = animation.frame_at(3)
            self.assertEqual(art.getpixel((20, 32)), (255, 243, 222))
            self.assertEqual(art.getpixel((75, 32)), (226, 136, 135))
            self.assertEqual(art.getpixel((44, 32)), animation.bg)

    def test_rgb_palette_uses_ink_masks_and_restores_fragment_colors(self):
        with tempfile.TemporaryDirectory() as temp:
            config, _, _ = self.fixture(Path(temp))
            original = json.loads(config.read_text())
            config.write_text(json.dumps({**original, 'palette': 'retro-print'}))
            animation = InkAnimation(config)
            art = animation.frame_at(3.2)
            self.assertGreater(len(animation.fragments), 0)
            self.assertEqual(art.getpixel((0, 0)), (245, 232, 212))
            self.assertEqual(art.getpixel((14, 36)), (174, 52, 42))
            self.assertEqual(art.getpixel((85, 48)), (40, 63, 100))
            self.assertEqual(art.tobytes(), animation.art.tobytes())

    def soft_edge_config(self, root, foreground, background):
        alpha = Image.new('L', (128, 96))
        draw = ImageDraw.Draw(alpha)
        for x, value in enumerate((16, 64, 128, 255, 255, 128, 64, 16), 20):
            draw.line((x, 20, x, 74), fill=value)
        rgba = Image.new('RGBA', alpha.size, (*foreground, 0))
        rgba.putalpha(alpha)
        rgba.save(root / 'rgba.png')
        Image.alpha_composite(
            Image.new('RGBA', alpha.size, (*background, 255)), rgba
        ).convert('RGB').save(root / 'rgb.png')
        alpha.point(lambda value: 255 if value else 0).save(root / 'first.png')
        return {'masks': {'first': 'first.png'}, 'background': background}

    def test_rgb_palette_keeps_soft_edges_like_equivalent_rgba_for_every_preset(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = self.soft_edge_config(root, (255, 255, 255), (0, 0, 0))
            for palette in PALETTES:
                with self.subTest(palette=palette):
                    outputs = []
                    animations = []
                    for mode in ('rgba', 'rgb'):
                        config = root / 'config.json'
                        config.write_text(json.dumps({
                            **original, 'art': mode + '.png', 'palette': palette,
                        }))
                        animation = InkAnimation(config)
                        animations.append(animation)
                        outputs.append(np.asarray(animation.frame_at(3)))
                    np.testing.assert_array_equal(outputs[0], outputs[1])
                    np.testing.assert_array_equal(
                        animations[0].first_times, animations[1].first_times)
                    for animation in animations:
                        self.assertEqual(animation.frame_at(0).getpixel((20, 40)), animation.bg)

    def test_dark_rgb_ink_on_a_light_backdrop_keeps_edge_opacity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = self.soft_edge_config(root, (30, 60, 80), (240, 235, 220))
            outputs = []
            for mode in ('rgba', 'rgb'):
                config = root / 'config.json'
                config.write_text(json.dumps({
                    **original, 'art': mode + '.png', 'palette': 'retro-print',
                }))
                animation = InkAnimation(config)
                frame = animation.frame_at(3)
                self.assertEqual(frame.getpixel((0, 0)), animation.bg)
                outputs.append(np.asarray(frame, dtype=np.int16))
            # Flattening onto an 8-bit backdrop introduces rounding, not solid edges.
            self.assertLessEqual(np.abs(outputs[0] - outputs[1]).max(), 2)
            self.assertGreater(len(np.unique(outputs[1][40, 20:28], axis=0)), 3)

    def test_unknown_palette_reports_available_names(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config = root / 'config.json'
            config.write_text(json.dumps({**self.palette_config(root), 'palette': 'typo'}))
            with self.assertRaisesRegex(ValueError, "Unknown signature palette 'typo'.*macaron"):
                InkAnimation(config)

    def test_user_start_and_timing_override_automatic_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            config, _, _ = self.fixture(Path(temp))
            cfg = json.loads(config.read_text())
            cfg['upper_pen'] = {'start_point':[115,16]}
            cfg['timing'] = {'upper_start':.1,'upper_end':.24}
            config.write_text(json.dumps(cfg))
            a = InkAnimation(config)
            self.assertEqual(a.upper_report['start_source'], 'configured start')
            self.assertEqual(a.upper_report['start_point'], [115,16])
            self.assertEqual(a.upper_report['start_seconds'], .1)

    def test_overlapping_layers_fail_instead_of_double_inking(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            config, _, _ = self.fixture(root)
            Image.open(root/'upper.png').save(root/'first.png')
            with self.assertRaisesRegex(ValueError, 'overlap'):
                InkAnimation(config)


if __name__ == '__main__':
    unittest.main()
