import pytest
import grblas as gb
import dask_grblas as dgb
from grblas import dtypes
from pytest import raises
from .utils import compare


@pytest.fixture
def vs():
    v = gb.Vector.from_values([0, 1, 2, 4, 5], [0, -20, 30, 40, 50])
    dv0 = dgb.Vector.from_vector(v)
    dv1 = dgb.concat_vectors(
        [
            dgb.Vector.from_vector(gb.Vector.from_values([0, 1, 2], [0, -20, 30])),
            dgb.Vector.from_vector(gb.Vector.from_values([1, 2], [40, 50])),
        ]
    )
    dv2 = dgb.concat_vectors(
        [
            dgb.concat_vectors(
                [
                    dgb.Vector.from_vector(gb.Vector.from_values([0], [0])),
                    dgb.Vector.from_vector(gb.Vector.from_values([0, 1], [-20, 30])),
                ]
            ),
            dgb.Vector.from_vector(gb.Vector.from_values([1, 2], [40, 50])),
        ]
    )
    return v, (dv0, dv1, dv2)


@pytest.fixture
def ws():
    w = gb.Vector.from_values([0, 1, 3, 4, 5], [1.0, 2.0, 3.0, -4.0, 0.0])
    dw0 = dgb.Vector.from_vector(w)
    dw1 = dgb.concat_vectors(
        [
            dgb.Vector.from_vector(gb.Vector.from_values([0, 1], [1.0, 2.0])),
            dgb.Vector.from_vector(gb.Vector.from_values([1, 2, 3], [3.0, -4.0, 0.0])),
        ]
    )
    return w, (dw0, dw1)


@pytest.fixture
def vms():
    val_mask = gb.Vector.from_values(
        [0, 1, 2, 3, 4, 5], [True, False, False, True, True, False], size=6
    )
    dvm0 = dgb.Vector.from_vector(val_mask)
    dvm1 = dgb.concat_vectors(
        [
            dgb.Vector.from_vector(gb.Vector.from_values([0, 1], [True, False])),
            dgb.Vector.from_vector(
                gb.Vector.from_values([0, 1, 2, 3], [False, True, True, False], size=4)
            ),
        ]
    )
    return val_mask, (dvm0, dvm1)


@pytest.fixture
def sms():
    struct_mask = gb.Vector.from_values([0, 3, 4], [False, False, False], size=6)

    dsm0 = dgb.Vector.from_vector(struct_mask)
    dsm1 = dgb.concat_vectors(
        [
            dgb.Vector.from_vector(gb.Vector.from_values([0], [False], size=2)),
            dgb.Vector.from_vector(
                gb.Vector.from_values([1, 2], [False, False], size=4)
            ),
        ]
    )
    return struct_mask, (dsm0, dsm1)


def test_new():
    v = gb.Vector.new(int)
    dv = dgb.Vector.new(int)
    compare(lambda x: x, v, dv)
    compare(lambda x: x.size, v, dv, compute=False)
    compare(lambda x: x.shape, v, dv, compute=False)
    v = gb.Vector.new(float, 3)
    dv = dgb.Vector.new(float, 3)
    compare(lambda x: x, v, dv)
    compare(lambda x: x.size, v, dv, compute=False)
    compare(lambda x: x.shape, v, dv, compute=False)
    o = object()
    compare(lambda x, y: type(x).new(y), (v, o), (dv, o), errors=True)


def test_dup(vs):
    v, dvs = vs
    for dv in dvs:
        compare(lambda x: x.dup(), v, dv)
        compare(lambda x: x.dup(dtype=dtypes.FP64), v, dv)
        o = object()
        compare(lambda x, y: x.dup(y), (v, o), (dv, o), errors=True)
        compare(lambda x: x.dup(mask=1), v, dv, errors=True)
    with raises(TypeError):
        dv.dup(mask=v.S)


@pytest.mark.slow
def test_isequal_isclose(vs, ws):
    o = object()
    for method_name in ["isequal", "isclose"]:
        v = vs[0]
        w = ws[0]
        for dv in vs[1]:
            compare(lambda x, y: getattr(x, method_name)(y), (v, v), (dv, dv))
            compare(lambda x: getattr(x, method_name)(o), v, dv, errors=True)
            for dw in ws[1]:
                compare(lambda x, y: getattr(x, method_name)(y), (v, w), (dv, dw))


def test_nvals(vs):
    v, dvs = vs
    for dv in dvs:
        compare(lambda x: x.nvals, v, dv)
    v = gb.Vector.new(int)
    dv = dgb.Vector.new(int)
    compare(lambda x: x.nvals, v, dv)


def test_clear(vs):
    def f(x):
        x.clear()
        return x

    v, dvs = vs
    compare(f, v, dvs[0])


def test_ewise(vs, ws):
    v = vs[0]
    w = ws[0]
    binfunc = lambda x, y: getattr(x, method_name)(y, op, require_monoid=False).new()
    for op in [gb.monoid.plus, gb.binary.plus]:
        for method_name in ["ewise_add", "ewise_mult"]:

            def f(w, x, y):
                w << getattr(x, method_name)(y, op)
                return w

            # errors = method_name == 'ewise_add' and op is gb.binary.plus
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
            for dv in vs[1]:
                for index, func in enumerate(funcs):
                    compare(func, (v, v), (dv, dv), errors=errors, compute=compute)
                if method_name == "ewise_add":
                    compare(binfunc, (v, v), (dv, dv))
                compare(
                    f,
                    (v.dup(), v, v),
                    (dv.dup(), dv, dv),
                    errors=errors,
                    compute=compute,
                )
                for dw in ws[1]:
                    for func in funcs:
                        compare(func, (v, w), (dv, dw), errors=errors, compute=compute)
                    if method_name == "ewise_add":
                        compare(binfunc, (v, v), (dv, dv))
                    compare(
                        f,
                        (v.dup(), v, w),
                        (dv.dup(), dv, dw),
                        errors=errors,
                        compute=compute,
                    )
                    compare(
                        f,
                        (w.dup(), v, w),
                        (dw.dup(), dv, dw),
                        errors=errors,
                        compute=compute,
                    )


def test_reduce(vs):
    v, dvs = vs

    def f0(x, y):
        x << y.reduce()
        return x

    def f1(x, y):
        x() << y.reduce()
        return x

    def f2(x, y):
        x(accum=gb.binary.plus) << y.reduce()
        return x

    for dv in dvs:
        compare(lambda x: x.reduce().new(), v, dv)
        compare(lambda x: x.reduce(gb.monoid.max).new(), v, dv)
        compare(lambda x: x.reduce().new(dtype=dtypes.FP64), v, dv)
        compare(lambda x: x.reduce(gb.binary.plus).new(), v, dv)
        for i, f in enumerate([f0, f1, f2]):
            s = gb.Scalar.new(int)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, v), (ds, dv))

            s = gb.Scalar.from_value(100)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, v), (ds, dv))

            s = gb.Scalar.new(float)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, v), (ds, dv))

            s = gb.Scalar.from_value(1.23)
            ds = dgb.Scalar.from_value(s.dup())
            compare(f, (s, v), (ds, dv))


def test_apply(vs):
    v, dvs = vs

    def f(x):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.unary.abs)
        return y

    def g(x, scalar=1):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.binary.gt, right=scalar)
        return y

    def h(x, scalar=2):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.binary.minus, left=scalar)
        return y

    def i(x, scalar=1):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.binary.plus, left=scalar)
        return y

    def j(x, scalar=1):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.monoid.plus, left=scalar)
        return y

    def k(x, scalar=1):
        y = type(x).new(x.dtype, x.size)
        y << x.apply(gb.monoid.plus, right=scalar)
        return y

    for dv in dvs:
        compare(lambda x: x.apply(gb.unary.abs).new(), v, dv)
        compare(lambda x: x.apply(gb.unary.abs).new(dtype=float), v, dv)
        compare(lambda x: x.apply(gb.binary.plus).new(), v, dv, errors=True)
        compare(f, v.dup(), dv.dup())

        compare(lambda x: x.apply(gb.binary.gt, right=1).new(), v, dv)
        compare(lambda x: x.apply(gb.binary.gt, right=1).new(dtype=float), v, dv)
        compare(g, v.dup(), dv.dup())
        s = gb.Scalar.from_value(1)
        ds = dgb.Scalar.from_value(s)
        compare(
            lambda x, s: x.apply(gb.binary.gt, right=s).new(dtype=float),
            (v, s),
            (dv, ds),
        )
        compare(g, (v.dup(), s), (dv.dup(), ds))

        compare(lambda x: x.apply(gb.binary.minus, left=2).new(), v, dv)
        compare(lambda x: x.apply(gb.binary.minus, left=2).new(dtype=float), v, dv)
        compare(h, v.dup(), dv.dup())
        s = gb.Scalar.from_value(2)
        ds = dgb.Scalar.from_value(s)
        compare(
            lambda x, s: x.apply(gb.binary.minus, left=s).new(dtype=float),
            (v, s),
            (dv, ds),
        )
        compare(h, (v.dup(), s), (dv.dup(), ds))

        compare(lambda x: x.apply(gb.binary.plus, left=1).new(), v, dv)
        compare(lambda x: x.apply(gb.binary.plus, left=1).new(dtype=float), v, dv)
        compare(i, v.dup(), dv.dup())
        s = gb.Scalar.from_value(1)
        ds = dgb.Scalar.from_value(s)
        compare(
            lambda x, s: x.apply(gb.binary.minus, left=s).new(dtype=float),
            (v, s),
            (dv, ds),
        )
        compare(i, (v.dup(), s), (dv.dup(), ds))

        compare(lambda x: x.apply(gb.monoid.plus, left=1).new(), v, dv)
        compare(lambda x: x.apply(gb.monoid.plus, left=1).new(dtype=float), v, dv)
        compare(j, v.dup(), dv.dup())
        s = gb.Scalar.from_value(1)
        ds = dgb.Scalar.from_value(s)
        compare(
            lambda x, s: x.apply(gb.binary.minus, left=s).new(dtype=float),
            (v, s),
            (dv, ds),
        )
        compare(j, (v.dup(), s), (dv.dup(), ds))

        compare(lambda x: x.apply(gb.monoid.plus, right=1).new(), v, dv)
        compare(lambda x: x.apply(gb.monoid.plus, right=1).new(dtype=float), v, dv)
        compare(k, v.dup(), dv.dup())
        s = gb.Scalar.from_value(1)
        ds = dgb.Scalar.from_value(s)
        compare(
            lambda x, s: x.apply(gb.binary.minus, right=s).new(dtype=float),
            (v, s),
            (dv, ds),
        )
        compare(k, (v.dup(), s), (dv.dup(), ds))


def test_update(vs, ws):
    v, dvs = vs
    w, dws = ws

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
        for dv in dvs:
            for dw in dws:
                compare(f, (v.dup(), w.dup()), (dv.dup(), dw.dup()))
                compare(
                    f, (v.dup(dtype=float), w.dup()), (dv.dup(dtype=float), dw.dup())
                )


def test_extract(vs, ws, vms, sms):
    v, dvs = vs
    w, dws = ws
    vm, dvms = vms
    sm, dsms = sms

    for index in [
        [0, 3, 1, 4, 2, 5],
        [0, 5, 5, 1, 2, 0],
        slice(None),
        slice(None, None, -1),
        [0] * 6,
    ]:

        def f(x, y):
            x << y[index]
            return x

        def g(x, y):
            x(accum=gb.binary.plus) << y[index]
            return x

        def h(m, x, y):
            x(mask=m, accum=gb.binary.plus) << y[index]
            return x

        def i(x, y):
            x[index] << y
            return x

        for dv in dvs:
            compare(lambda x: x[index].new(), v, dv)
            compare(lambda x: x[index].new(dtype=float), v, dv)
            for dw in dws:
                compare(f, (v.dup(), w), (dv.dup(), dw))
                compare(f, (v.dup(dtype=float), w), (dv.dup(dtype=float), dw))
                compare(g, (v.dup(), w), (dv.dup(), dw))
                compare(g, (v.dup(dtype=float), w), (dv.dup(dtype=float), dw))
                for dvm in dvms:
                    compare(h, (vm.V, v.dup(), w), (dvm.V, dv.dup(), dw))
                    compare(
                        h,
                        (vm.V, v.dup(dtype=float), w),
                        (dvm.V, dv.dup(dtype=float), dw),
                    )
                for dsm in dsms:
                    compare(h, (vm.S, v.dup(), w), (dvm.S, dv.dup(), dw))
                    compare(
                        h,
                        (vm.S, v.dup(dtype=float), w),
                        (dvm.S, dv.dup(dtype=float), dw),
                    )


@pytest.mark.xfail
def test_attrs(vs):
    v, dvs = vs
    dv = dvs[0]
    assert set(dir(v)) - set(dir(dv)) == {
        "__del__",  # TODO
        "_assign_element",
        "_extract_element",
        "_is_scalar",
        "_prep_for_assign",
        "_prep_for_extract",
        "_delete_element",
        "gb_obj",
        "show",
    }
    assert set(dir(dv)) - set(dir(v)) == {
        "_delayed",
        "_meta",
        "_optional_dup",
        "compute",
        "from_vector",
        "from_delayed",
        "persist",
        "visualize",
    }
