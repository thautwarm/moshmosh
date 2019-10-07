"""
The original idea is originated from
    https://github.com/asottile/future-fstrings
"""
from moshmosh.extension import extension
import codecs
import encodings
import io

utf_8 = encodings.search_function('utf8')


def rewrite(text, errors='strict'):
    u, length = utf_8.decode(text, errors)
    u = extension(u)
    return u, length


class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
    def _buffer_decode(self, input, errors, final):  # pragma: no cover
        if final:
            return rewrite(input, errors)
        else:
            return '', 0


class StreamReader(utf_8.streamreader, object):
    """decode is deferred to support better error messages"""
    _stream = None
    _decoded = False

    @property
    def stream(self):
        if not self._decoded:
            text, _ = rewrite(self._stream.read())
            self._stream = io.BytesIO(text.encode('UTF-8'))
            self._decoded = True
        return self._stream

    @stream.setter
    def stream(self, stream):
        self._stream = stream
        self._decoded = False


codec_map = {
    name: codecs.CodecInfo(
        name=name,
        encode=utf_8.encode,
        decode=rewrite,
        incrementalencoder=utf_8.incrementalencoder,
        incrementaldecoder=IncrementalDecoder,
        streamreader=StreamReader,
        streamwriter=utf_8.streamwriter,
    )
    for name in ('extension', )
}

codecs.register(codec_map.get)