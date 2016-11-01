# -*- coding: utf-8 -*-

import click

from m3u_dump.m3u_dump import M3uDump


@click.command()
@click.argument('load-m3u-path', type=click.Path(exists=True))
@click.argument('dump-music-path')
@click.option('--dry-run/--no-dry-run', default=False, help='Dry run')
@click.option('--with-playlist/--no-with-playlist', default=True, help='too copy fixed playlist')
@click.option('--fix-search-path', default=None, help='fix search path')
@click.option('--playlist-pattern-list', default=['*.m3u', '*.m3u8'])
def main(**kwargs):
    """Console script for m3u_dump"""

    click.echo(click.style('=' * 53, fg='green'))
    click.echo(click.style('   Welcome m3u-dump!!', fg='green'))
    click.echo(click.style('=' * 53, fg='green'))

    M3uDump(kwargs).start()

    click.echo()
    click.echo(click.style('copy was completed(successful!).'))

if __name__ == "__main__":
    main()
