import pytest
import grblas as gb
import dask_grblas as dgb
from grblas import dtypes
from pytest import raises
from .utils import compare
from functools import partial
from builtins import getattr


@pytest.fixture
def vs():
    v = gb.Vector.from_values([0, 1, 2, 4, 6], [0, -20, 30, 40, 50])
    dv0 = dgb.Vector.from_vector(v)
    dv1 = dgb.concat_vectors([
        dgb.Vector.from_vector(gb.Vector.from_values([0, 1, 2], [0, -20, 30])),
        dgb.Vector.from_vector(gb.Vector.from_values([1, 3], [40, 50])),
    ])
    dv2 = dgb.concat_vectors([
        dgb.concat_vectors([
            dgb.Vector.from_vector(gb.Vector.from_values([0], [0])),
            dgb.Vector.from_vector(gb.Vector.from_values([0, 1], [-20, 30])),
        ]),
        dgb.Vector.from_vector(gb.Vector.from_values([1, 3], [40, 50])),
    ])
    return v, (dv0, dv1, dv2)


@pytest.fixture
def ws():
    w = gb.Vector.from_values([0, 1, 3, 4, 6], [1.0, 2.0, 3.0, -4.0, 0.0])
    dw0 = dgb.Vector.from_vector(w)
    dw1 = dgb.concat_vectors([
        dgb.Vector.from_vector(gb.Vector.from_values([0, 1], [1.0, 2.0])),
        dgb.Vector.from_vector(gb.Vector.from_values([1, 2, 4], [3.0, -4.0, 0.0])),
    ])
    return w, (dw0, dw1)


@pytest.fixture
def vms():
    val_mask = gb.Vector.from_values(
        [0, 1, 2, 3, 4],
        [True, False, False, True, True],
        size=7)
    dvm0 = dgb.Vector.from_vector(val_mask)
    dvm1 = dgb.concat_vectors([
        dgb.Vector.from_vector(
            gb.Vector.from_values([0, 1], [True, False])),
        dgb.Vector.from_vector(
            gb.Vector.from_values([0, 1, 2], [False, True, True], size=5)),
    ])
    return val_mask, (dvm0, dvm1)


@pytest.fixture
def sms():
    struct_mask = gb.Vector.from_values(
        [0, 3, 4],
        [False, False, False],
        size=7)

    dsm0 = dgb.Vector.from_vector(struct_mask)
    dsm1 = dgb.concat_vectors([
        dgb.Vector.from_vector(
            gb.Vector.from_values([0], [False], size=2)),
        dgb.Vector.from_vector(
            gb.Vector.from_values([1, 2], [False, False], size=5)),
    ])
    return struct_mask, (dsm0, dsm1)


@pytest.fixture
def As():
    #    0 1 2 3 4 5 6
    # 0 [- 2 - 3 - - -]
    # 1 [- - - - 8 - 4]
    # 2 [- - - - - 1 -]
    # 3 [3 - 3 - - - -]
    # 4 [- - - - - 7 -]
    # 5 [- - 1 - - - -]
    # 6 [- - 5 7 3 - -]
    data = [
        [3, 0, 3, 5, 6, 0, 6, 1, 6, 2, 4, 1],
        [0, 1, 2, 2, 2, 3, 3, 4, 4, 5, 5, 6],
        [3, 2, 3, 1, 5, 3, 7, 8, 3, 1, 7, 4],
    ]
    A = gb.Matrix.from_values(*data)
    dA0 = dgb.Matrix.from_matrix(A)
    
    dA1 = dgb.row_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([3, 0, 3, 0, 1, 2, 1],
                                  [0, 1, 2, 3, 4, 5, 6],
                                  [3, 2, 3, 3, 8, 1, 4])),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 2, 2, 2, 0],
                                  [2, 2, 3, 4, 5],
                                  [1, 5, 7, 3, 7], ncols=7))])

    dA2 = dgb.row_stack([
        dgb.row_stack([
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([0, 0, 1, 1],
                                      [1, 3, 4, 6],
                                      [2, 3, 8, 4])),
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([1, 1, 0],
                                      [0, 2, 5],
                                      [3, 3, 1], ncols=7))]),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 2, 2, 2, 0],
                                  [2, 2, 3, 4, 5],
                                  [1, 5, 7, 3, 7], ncols=7))])

    dA3 = dgb.column_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([3, 0, 3, 5, 6, 0, 6],
                                  [0, 1, 2, 2, 2, 3, 3],
                                  [3, 2, 3, 1, 5, 3, 7])),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 6, 2, 4, 1],
                                  [0, 0, 1, 1, 2],
                                  [8, 3, 1, 7, 4]))])

    dA4 = dgb.column_stack([
        dgb.column_stack([
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([3, 0],
                                      [0, 1],
                                      [3, 2], nrows=7)),
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([3, 5, 6, 0, 6],
                                      [0, 0, 0, 1, 1],
                                      [3, 1, 5, 3, 7]))]),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 6, 2, 4, 1],
                                  [0, 0, 1, 1, 2],
                                  [8, 3, 1, 7, 4]))])

    dA5 = dgb.row_stack([
        dgb.column_stack([
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([3, 0, 3, 0],
                                      [0, 1, 2, 3],
                                      [3, 2, 3, 3])),
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([1, 2, 1],
                                      [0, 1, 2],
                                      [8, 1, 4], nrows=4))]),
        dgb.column_stack([
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([1, 2, 2],
                                      [2, 2, 3],
                                      [1, 5, 7])),
            dgb.Matrix.from_matrix(
                gb.Matrix.from_values([2, 0],
                                      [0, 1],
                                      [3, 7], ncols=3))])])

    return A, (dA0, dA1, dA2, dA3, dA4, dA5)


@pytest.fixture
def Cs():
    #    0 1 2 3 4 5 6
    # 0 [- 2 - 3 - - -]
    # 1 [- - - - - - 4]
    # 2 [- - 4 - - 1 -]
    # 3 [3 - 3 - - - -]
    # 4 [- - - - - 7 -]
    # 5 [- - 1 - - - -]
    # 6 [- - 5 7 3 - -]
    data = [
        [3, 0, 3, 5, 6, 0, 6, 2, 6, 2, 4, 1],
        [0, 1, 2, 2, 2, 3, 3, 2, 4, 5, 5, 6],
        [3, 2, 3, 1, 5, 3, 7, 4, 3, 1, 7, 4],
    ]
    C = gb.Matrix.from_values(*data)
    dC0 = dgb.Matrix.from_matrix(C)
    
    dC1 = dgb.row_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([3, 0, 3, 0, 2, 2, 1],
                                  [0, 1, 2, 3, 2, 5, 6],
                                  [3, 2, 3, 3, 4, 1, 4])),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 2, 2, 2, 0],
                                  [2, 2, 3, 4, 5],
                                  [1, 5, 7, 3, 7], ncols=7))])

    dC2 = dgb.column_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([3, 0, 3, 5, 6, 0, 6, 2],
                                  [0, 1, 2, 2, 2, 3, 3, 2],
                                  [3, 2, 3, 1, 5, 3, 7, 4])),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([6, 2, 4, 1],
                                  [0, 1, 1, 2],
                                  [3, 1, 7, 4]))])

    return C, (dC0, dC1, dC2)


@pytest.fixture
def Bs():
    #    |   0    1    2    3    4    5    6    7    8    9    10   11
    # ___|____________________________________________________________
    # 0  |       1.0  1.0  1.0                        
    # 1  |  1.0       1.0                           
    # 2  |  1.0  1.0            1.0  1.0                  
    # 3  |  1.0                 1.0                     
    # 4  |            1.0  1.0                        
    # 5  |            1.0                           
    # 6  |                                     1.0  1.0         
    # 7  |                                1.0               
    # 8  |                                1.0               
    # 9  |                                                    1.0  1.0
    # 10 |                                               1.0      
    # 11 |                                               1.0      
    data = [
        [0, 0, 0, 1, 2, 2, 3, 6, 6,  9,  9, 1, 2, 3, 2, 4, 5, 4, 7, 8, 10, 11],
        [1, 2, 3, 2, 4, 5, 4, 7, 8, 10, 11, 0, 0, 0, 1, 2, 2, 3, 6, 6,  9,  9],
        [1.0]*22
    ]
    B = gb.Matrix.from_values(*data)
    dB0 = dgb.Matrix.from_matrix(B)
    
    dB1 = dgb.row_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([0, 0, 0, 1, 2, 2, 3, 6, 6, 1, 2, 3, 2, 4, 5, 4],
                                  [1, 2, 3, 2, 4, 5, 4, 7, 8, 0, 0, 0, 1, 2, 2, 3],
                                  [1.0]*16, ncols=12)),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([2,   2, 0, 1, 3, 4],
                                  [10, 11, 6, 6, 9, 9],
                                  [1.0]*6))])

    dB2 = dgb.column_stack([
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([1, 2, 3, 2, 4, 5, 4, 7, 8, 0, 0, 0, 1, 2, 2, 3],
                                  [0, 0, 0, 1, 2, 2, 3, 6, 6, 1, 2, 3, 2, 4, 5, 4],
                                  [1.0]*16, nrows=12)),
        dgb.Matrix.from_matrix(
            gb.Matrix.from_values([10, 11, 6, 6, 9, 9],
                                  [2,   2, 0, 1, 3, 4],
                                  [1.0]*6))])

    return B, (dB0, dB1, dB2)


def test_new():
    A = gb.Matrix.new(int)
    dA = dgb.Matrix.new(int)
    compare(lambda x: x, A, dA)
    compare(lambda x: x.nrows, A, dA, compute=False)
    compare(lambda x: x.ncols, A, dA, compute=False)
    compare(lambda x: x.shape, A, dA, compute=False)
    A = gb.Matrix.new(float, 3, 4)
    dA = dgb.Matrix.new(float, 3, 4)
    compare(lambda x: x, A, dA)
    compare(lambda x: x.nrows, A, dA, compute=False)
    compare(lambda x: x.ncols, A, dA, compute=False)
    compare(lambda x: x.shape, A, dA, compute=False)
    o = object()
    compare(lambda x, y: type(x).new(y), (A, o), (dA, o), errors=True)


def test_dup(As):
    A, dAs = As
    for dA in dAs:
        compare(lambda x: x.dup(), A, dA)
        compare(lambda x: x.dup(dtype=dtypes.FP64), A, dA)
        o = object()
        compare(lambda x, y: x.dup(y), (A, o), (dA, o), errors=True)
        compare(lambda x: x.dup(mask=1), A, dA, errors=True)
    with raises(TypeError):
        dA.dup(mask=A.S)


@pytest.mark.slow
def test_isequal_isclose(As, Bs):
    o = object()
    for method_name in ['isequal', 'isclose']:
        A = As[0]
        B = Bs[0]
        for dA in As[1]:
            compare(lambda x, y: getattr(x, method_name)(y), (A, A), (dA, dA))
            compare(lambda x: getattr(x, method_name)(o), A, dA, errors=True)
            for dB in Bs[1]:
                compare(lambda x, y: getattr(x, method_name)(y), (A, B), (dA, dB))


def test_nvals(As):
    A, dAs = As
    for dA in dAs:
        compare(lambda x: x.nvals, A, dA)
    A = gb.Vector.new(int)
    dA = dgb.Vector.new(int)
    compare(lambda x: x.nvals, A, dA)


def test_clear(As):

    def f(x):
        x.clear()
        return x

    A, dAs = As
    compare(f, A, dAs[0])


@pytest.mark.slow
def test_ewise(As, Cs):
    A = As[0]
    C = Cs[0]
    binfunc = lambda x, y: getattr(x, method_name)(y, op, require_monoid=False).new()
    for op in [gb.monoid.plus, gb.binary.plus]:
        for method_name in ['ewise_add', 'ewise_mult']:

            def f(C, x, y):
                C << getattr(x, method_name)(y, op)
                return C

            errors = False
            compute = not errors
            funcs = [
                lambda x, y: getattr(x, method_name)(y, op).new(),
                lambda x, y: getattr(x, method_name)(y, op).new(dtype=dtypes.FP64),
                lambda x, y: getattr(x, method_name)(y, op).new(mask=y.S),
                lambda x, y: getattr(x, method_name)(y, op).new(mask=y.V),
                lambda x, y: getattr(x, method_name)(y, op).new(mask=~x.S),
                lambda x, y: getattr(x, method_name)(y, op).new(mask=~x.V),
            ]
            for dA in As[1]:
                for index, func in enumerate(funcs):
                    compare(func, (A, A), (dA, dA), errors=errors, compute=compute)
                if method_name == 'ewise_add':
                    compare(binfunc, (A, A), (dA, dA))
                compare(f, (A.dup(), A, A), (dA.dup(), dA, dA), errors=errors, compute=compute)
                for dw in Cs[1]:
                    for func in funcs:
                        compare(func, (A, C), (dA, dw), errors=errors, compute=compute)
                    if method_name == 'ewise_add':
                        compare(binfunc, (A, A), (dA, dA))
                    compare(f, (A.dup(), A, C), (dA.dup(), dA, dw), errors=errors, compute=compute)
                    compare(f, (C.dup(), A, C), (dw.dup(), dA, dw), errors=errors, compute=compute)


@pytest.mark.slow
def test_reduce_axis(As, vs, ws):
    A, dAs = As

    def f0(method_name, x, y):
        x << getattr(y, method_name)()
        return x

    def f1(method_name, x, y):
        x() << getattr(y, method_name)()
        return x

    def f2(method_name, x, y):
        x(accum=gb.binary.plus) << getattr(y, method_name)()
        return x

    for dA in dAs:
        for method_name in ['reduce_rowwise', 'reduce_columnwise']:
            compare(lambda x: getattr(x, method_name)().new(), A, dA)
            compare(lambda x: getattr(x, method_name)(gb.monoid.max).new(), A, dA)
            compare(lambda x: getattr(x, method_name)().new(dtype=dtypes.FP64), A, dA)
            compare(lambda x: getattr(x, method_name)(gb.binary.plus).new(), A, dA)
            for func in [f0, f1, f2]:
                f = partial(func, method_name)
                v = gb.Vector.new(int, 7)
                dv = dgb.Vector.from_vector(v.dup())
                compare(f, (v, A), (dv, dA))
    
                v = gb.Vector.new(float, 7)
                dv = dgb.Vector.from_vector(v.dup())
                compare(f, (v, A), (dv, dA))
    
                v0, dvs = vs
                for dv0 in dvs:
                    v = v0.dup()
                    dv = dv0.dup()
                    compare(f, (v, A), (dv, dA))
        
                if f is not f2:
                    w0, dws = ws
                    for dw0 in dws:
                        w = w0.dup()
                        dw = dw0.dup()
                        compare(f, (w, A), (dw, dA))


@pytest.mark.slow
def test_reduce_scalar(As):
    A, dAs = As

    def f0(x, y):
        x << y.reduce_scalar()
        return x

    def f1(x, y):
        x() << y.reduce_scalar()
        return x

    def f2(x, y):
        x(accum=gb.binary.plus) << y.reduce_scalar()
        return x

    for dA in dAs:
        compare(lambda x: x.reduce_scalar().new(), A, dA)
        compare(lambda x: x.reduce_scalar(gb.monoid.max).new(), A, dA)
        compare(lambda x: x.reduce_scalar().new(dtype=dtypes.FP64), A, dA)
        compare(lambda x: x.reduce_scalar(gb.binary.plus).new(), A, dA)
        for i, f in enumerate([f0, f1, f2]):
            s = gb.Scalar.new(int)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, A), (ds, dA))

            s = gb.Scalar.from_value(100)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, A), (ds, dA))

            s = gb.Scalar.new(float)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, A), (ds, dA))

            if f is not f2:  # XXX: uncomment when updated to SS 3.3.1 and fixed in grblas
                s = gb.Scalar.from_value(1.23)
                ds = dgb.Scalar.from_value(s.dup())
                compare(f, (s, A), (ds, dA))


@pytest.mark.slow
def test_apply(As):
    A, dAs = As

    def f(x):
        y = type(x).new(x.dtype, nrows=x.nrows, ncols=x.ncols)
        y << x.apply(gb.unary.abs)
        return y

    for dA in dAs:
        compare(lambda x: x.apply(gb.unary.abs).new(), A, dA)
        compare(lambda x: x.apply(gb.unary.abs).new(dtype=float), A, dA)
        compare(lambda x: x.apply(gb.binary.plus).new(), A, dA, errors=True)
        compare(f, A.dup(), dA.dup())


@pytest.mark.slow
def test_update(As, Cs):
    A, dAs = As
    C, dCs = Cs

    def f0(x, y):
        x.update(y)
        return x

    def f1(x, y):
        x << y
        return x

    def f2(x, y):
        x().update(y)
        return x

    def f3(x, y):
        x(y.S) << y
        return x

    def f4(x, y):
        x(y.V) << y
        return x

    def f5(x, y):
        x(accum=gb.binary.plus).update(y)
        return x

    for f in [f0, f1, f2, f3, f4, f5]:
        for dA in dAs:
            for dC in dCs:
                compare(f, (A.dup(), C.dup()), (dA.dup(), dC.dup()))
                compare(f, (A.dup(dtype=float), C.dup()), (dA.dup(dtype=float), dC.dup()))


@pytest.mark.slow
def test_matmult(As, vs, ws, vms, sms):
    def f0(method_name, z, x, y):
        z << getattr(x, method_name)(y)
        return z

    def f1(method_name, z, x, y):
        z() << getattr(x, method_name)(y)
        return z

    def f2(method_name, z, x, y):
        z(accum=gb.binary.plus) << getattr(x, method_name)(y)
        return z

    def f3(method_name,z, m, x, y):
        z(mask=m, accum=gb.binary.plus) << getattr(x, method_name)(y)
        return z

    def f4(method_name,z, m, x, y):
        z(mask=m) << getattr(x, method_name)(y)
        return z

    A, dAs = As
    v, dvs = vs

    for dA in dAs:
        for dv in dvs:
            for method_name in ['mxv', 'vxm']:
                if method_name == 'mxv':
                    gb_args = (A, v)
                    dgb_args = (dA, dv)
                else:
                    gb_args = (v, A)
                    dgb_args = (dv, dA)

                compare(lambda x, y: getattr(x, method_name)(y).new(), gb_args, dgb_args)
                compare(lambda x, y: getattr(x, method_name)(y, gb.semiring.min_second).new(), gb_args, dgb_args)
                compare(lambda x, y: getattr(x, method_name)(y).new(dtype=dtypes.FP64), gb_args, dgb_args)
                compare(lambda x, y: getattr(x, method_name)(y, gb.binary.plus).new(), gb_args, dgb_args, errors=True)
                for func in [f0, f1, f2]:
                    f = partial(func, method_name)
                    v1 = gb.Vector.new(int, 7)
                    dv1 = dgb.Vector.from_vector(v1.dup())
                    compare(f, (v1, *gb_args), (dv1, *dgb_args))
                
                    v1 = gb.Vector.new(float, 7)
                    dv1 = dgb.Vector.from_vector(v1.dup())
                    compare(f, (v1, *gb_args), (dv1, *dgb_args))
                
                    v0, dv0s = vs
                    for dv0 in dv0s:
                        v1 = v0.dup()
                        dv1 = dv0.dup()
                        compare(f, (v1, *gb_args), (dv1, *dgb_args))
                
                    w0, dw0s = ws
                    for dw0 in dw0s:
                        w1 = w0.dup()
                        dw1 = dw0.dup()
                        compare(f, (w1, *gb_args), (dw1, *dgb_args))

                for f in [partial(f3, method_name), partial(f4, method_name)]:
                    for attr, mask, dmasks in [('V', *vms), ('S', *sms)]:
                        for dmask in dmasks:
                            gb_mask = getattr(mask, attr)
                            dgb_mask = getattr(dmask, attr)
    
                            v1 = gb.Vector.new(int, 7)
                            dv1 = dgb.Vector.from_vector(v1.dup())
                            compare(f, (v1, gb_mask, *gb_args), (dv1, dgb_mask, *dgb_args))
                            compare(f, (v1, ~gb_mask, *gb_args), (dv1, ~dgb_mask, *dgb_args))
    
                            v1 = gb.Vector.new(float, 7)
                            dv1 = dgb.Vector.from_vector(v1.dup())
                            compare(f, (v1, gb_mask, *gb_args), (dv1, dgb_mask, *dgb_args))
                            compare(f, (v1, ~gb_mask, *gb_args), (dv1, ~dgb_mask, *dgb_args))
    
                            v0, dv0s = vs
                            for dv0 in dv0s:
                                v1 = v0.dup()
                                dv1 = dv0.dup()
                                compare(f, (v1, gb_mask, *gb_args), (dv1, dgb_mask, *dgb_args))
                                compare(f, (v1, ~gb_mask, *gb_args), (dv1, ~dgb_mask, *dgb_args))
    
                            w0, dw0s = ws
                            for dw0 in dw0s:
                                w1 = w0.dup()
                                dw1 = dw0.dup()
                                compare(f, (w1, gb_mask, *gb_args), (dw1, dgb_mask, *dgb_args))
                                compare(f, (w1, ~gb_mask, *gb_args), (dw1, ~dgb_mask, *dgb_args))


def test_attrs(vs):
    A, dvs = vs
    dv = dvs[0]
    assert set(dir(A)) - set(dir(dv)) == {
        '__del__',  # TODO
        '_assign_element', '_extract', '_extract_element', '_is_scalar', '_prep_for_assign',
        '_prep_for_extract', '_delete_element', 'gb_obj', 'show',
    }
    assert set(dir(dv)) - set(dir(A)) == {
        '_delayed', '_meta', '_optional_dup',
        'compute', 'from_vector', 'from_delayed', 'persist', 'visualize',
    }