package shapes;

public class ShapeTest {

	public static void main(String[] args) {
		Shape shape = new Circle("blue",10,20,10.0);
		System.out.println("shape的周长为："+ shape.getPerimeter());
		System.out.println("shape的面积为："+ shape.getArea());
		System.out.println("shape的颜色为"+shape.getColor());
		shape.move(15,25);
		Circle circle=(Circle)shape;
		System.out.println(circle.getCenter());
	}
}
